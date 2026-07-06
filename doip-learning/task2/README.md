# 任务 2：DoIP 模拟器 + UDS 业务逻辑

> 对应学习计划第 2 周。任务 1 已会看 DoIP 封装；任务 2 把 **CAN UDS 经验接到以太网** 上。  
> **全部任务总览**：[../README.md](../README.md)（在 `doip-learning/` 根目录，不在 task3 内）

## 与任务 1 的区别

| 维度 | 任务 1 | 任务 2 |
|------|--------|--------|
| TCP 收到 0x8001 后 | 只回 0x8002 Ack | **0x8002 Ack + 0x8001 携带 UDS 正/负响应** |
| UDS 服务 | 无真实处理 | **0x10 会话、0x22 读 DID、NRC** |
| 学习目标 | 看懂 DoIP 传输 | **验证 UDS 层与 CAN 完全一致，只多一层 DoIP 头** |

## 任务清单

| 编号 | 内容 | 脚本 |
|------|------|------|
| 2.1 | DoIP 模拟器（UDP 发现 + TCP 激活） | 复用 task1 的 `doip_udp_server.py` + 本目录 `doip_tcp_server_uds.py` |
| 2.2 | 接入 UDS：0x10 / 0x22 / NRC | `uds_ecu.py` + `doip_client_uds.py` |

## 快速开始（Windows 本机）

路径示例：

```powershell
cd "E:\Cache\Cursor\Embedded Study Project\EmbeddedStudyProject"
git pull
git checkout cursor/doip-task2-8401
```

### 终端 1 — UDP 发现（与任务 1 相同）

```powershell
cd doip-learning\task1\scripts
py doip_udp_server.py
```

### 终端 2 — 带 UDS 的 TCP 服务（任务 2 新）

```powershell
cd doip-learning\task2\scripts
py doip_tcp_server_uds.py
```

### 终端 3 — 完整 UDS 测试客户端

```powershell
cd doip-learning\task2\scripts
py doip_client_uds.py --host 127.0.0.1
```

可选：Wireshark 抓 loopback，过滤器 `tcp.port == 13400`。

## 客户端会自动跑哪些用例

| 步骤 | UDS 请求 | 期望结果 |
|------|----------|----------|
| 1 | `10 01` | `50 01` 进入默认会话 |
| 2 | `22 F1 90` | `62 F1 90` + VIN |
| 3 | `22 F1 86` | `62 F1 86` + 当前会话 |
| 4 | `22 F1 87` | **NRC 0x22**（默认会话不允许读） |
| 5 | `10 03` | `50 03` 进入扩展会话 |
| 6 | `22 F1 87` | `62 F1 87` + 零件号 |
| 7 | `22 FF FF` | **NRC 0x31** 未知 DID |
| 8 | `99 00` | **NRC 0x11** 服务不支持 |

## Wireshark 里多看什么

每个 UDS 请求在 TCP 上应看到 **两条下行**：

```
Tester -> ECU   0x8001  [UDS 请求]
ECU -> Tester   0x8002  Ack
ECU -> Tester   0x8001  [UDS 响应或 7F ... NRC]
```

这与 CAN 诊断仪看到的 UDS 字节 **相同**，只是外面包了 DoIP 头。

## 内置 DID 表（模拟车灯 ECU）

| DID | 含义 | 访问条件 |
|-----|------|----------|
| F190 | VIN | 默认会话可读 |
| F186 | 当前诊断会话 | 默认会话可读 |
| F187 | 零件号 demo | **仅扩展会话 0x03** |

## 目录结构

```
task2/
├── README.md
└── scripts/
    ├── _import_path.py          # 引用 task1 的 doip_common
    ├── uds_ecu.py               # UDS 状态机 + DID + NRC
    ├── doip_tcp_server_uds.py   # DoIP + UDS 服务端
    ├── doip_client_uds.py       # 自动化测试客户端
    └── test_uds_ecu.py          # 本地单元自检
```

## 自测清单（任务 2 完成标准）

- [ ] 能说出：DoIP 层多了哪两步（0x8002 + 0x8001 响应）
- [ ] Wireshark 里找到 `7F 22 31`（NRC）并解释含义
- [ ] 能修改 `uds_ecu.py` 增加一个 DID 并用 `22` 读出来
- [ ] 理解：换到 CAN UDS，只需去掉 DoIP 头，UDS  payload 不变

## 下一步（任务 3 预告）

- 错误源地址、Alive Check 超时、TCP 断连重连
- 对照真实 ECU 抓包与模拟器差异
