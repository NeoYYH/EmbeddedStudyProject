# Wireshark 抓包指南（任务 1.1）

## 1. 抓哪张网卡？

本实验脚本默认 `127.0.0.1`，请抓 **回环接口**：

| 系统 | 接口名 |
|------|--------|
| Linux | `Loopback: lo` |
| Windows | `Npcap Loopback Adapter` 或类似名称 |
| macOS | `Loopback` |

若后续对接真实 ECU 或另一台机器，改抓实际以太网网卡（如 `eth0`、车载诊断用的网卡）。

## 2. 推荐过滤器

### 只看 DoIP 端口

```
udp.port == 13400 || tcp.port == 13400
```

### 只看 TCP 握手

```
tcp.port == 13400 && tcp.flags.syn == 1
```

### 追踪某次 TCP 会话

右键某条 TCP 包 → **Follow → TCP Stream**，可看到路由激活和诊断报文的完整字节流。

## 3. 逐步对照：一次完整客户端运行

运行 `python3 doip_client.py` 后，按时间顺序在 Wireshark 中找以下阶段。

### 阶段 A — UDP 车辆发现（无握手）

| 方向 | 协议 | 关键字段 |
|------|------|----------|
| Client → Server | UDP | 目的端口 13400，Payload 以 `02 FD 00 01` 开头 |
| Server → Client | UDP | Payload 以 `02 FD 00 02` 开头，含 17 字节 VIN |

**DoIP 通用头（8 字节）**：

```
02 FD          Protocol Version / Inverse Version
00 01          Payload Type (Vehicle Identification Request)
00 00 00 00    Payload Length = 0
```

**为什么用 UDP？**

- 发现阶段不知道 ECU IP，常配合广播/多播或网段扫描。
- 单次请求-响应即可，无需维持连接。
- 失败成本低，可快速超时重试。

### 阶段 B — TCP 三次握手

在第一条 DoIP TCP 报文（`0x0005`）**之前**，应看到：

```
Client → Server   SYN
Server → Client   SYN, ACK
Client → Server   ACK
```

**为什么诊断走 TCP？**

- UDS 会话可能持续数分钟，需要可靠、有序的字节流。
- 路由激活后逻辑地址与 TCP 连接绑定，便于 Alive Check 与多帧诊断。
- ISO-TP 在 CAN 上做的分包/流控，在以太网侧由 TCP 承担传输可靠性。

### 阶段 C — 路由激活（0x0005 / 0x0006）

TCP 载荷以 `02 FD 00 05` 开头为 Routing Activation Request。

典型请求 payload（11 字节）：

| 偏移 | 长度 | 含义 |
|------|------|------|
| 0 | 2 | Source Address（测试仪逻辑地址，如 0x0E80） |
| 2 | 1 | Activation Type（0x00 = Default） |
| 3 | 4 | Reserved |
| 7 | 4 | OEM Specific（可选） |

响应 `0x0006` 中 **Response Code 0x10** 表示路由激活成功。

### 阶段 D — 诊断报文（0x8001 / 0x8002）

示例 UDS `10 01`（默认会话）封装在 Diagnostic Message 中：

```
02 FD 80 01 00 00 00 06   # Header: type=0x8001, len=6
0E 80 0E 00 10 01         # SrcAddr, TgtAddr, UDS payload
```

ECU 可先回 **0x8002** 肯定确认，再回 **0x8001** 携带 UDS 正响应（本模拟器任务 1 仅演示 Ack）。

## 4. 与 CAN UDS 抓包对比（建立直觉）

| 维度 | CAN UDS | DoIP |
|------|---------|------|
| 寻址 | CAN ID + 可能 ISO-TP | IP + 逻辑地址（路由激活后） |
| 传输 | 单帧 / 多帧 ISO-TP | TCP 字节流 + DoIP 头 |
| 发现 | 无（固定 ID） | UDP Vehicle Identification |
| 会话保持 | 总线一直在线 | TCP 连接 + Alive Check |

你在 CAN 上熟悉的 **0x10/0x22/0x27** 在 DoIP 里只是 `0x8001` 的 payload，业务语义不变。

## 5. 常见问题

**Q: Wireshark 没有 DoIP 解码列？**  
A: 版本较新的一般自带。没有时用 `tcp.port == 13400` + 十六进制视图手动看 `02 FD` 头。

**Q: 看不到 UDP 包？**  
A: 确认 `doip_udp_server.py` 已启动，且抓的是 lo；防火墙未拦 13400。

**Q: 有 TCP 握手但没有 0x0005？**  
A: 检查客户端是否连错端口，或服务器是否在 `accept` 后崩溃。

## 6. 任务 1.1 完成标准

- [ ] 能在一屏 Wireshark 里指出：哪几条是握手、哪条是 0x0001、哪条是 0x0005、哪条是 0x8001
- [ ] 能向他人解释：发现为何 UDP、诊断为何 TCP（各至少 2 条理由）
- [ ] 保存一份 `.pcapng` 备查（File → Save As）
