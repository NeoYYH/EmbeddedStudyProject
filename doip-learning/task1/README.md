# 任务 1：DoIP 基础 + 协议文档

> 对应学习计划第 1 周。完成后应能用 Wireshark 区分 UDP 发现与 TCP 诊断传输，并画出完整 DoIP 时序图。  
> **总览**：[../LEARNING_PLAN.md](../LEARNING_PLAN.md)

## 任务清单

| 编号 | 内容 | 状态 |
|------|------|------|
| 1.1 | Wireshark 抓包：TCP 三次握手 vs UDP 无连接 | 本目录脚本已就绪 |
| 1.2 | 精读 ISO 13400-2 + 手绘/标注 DoIP 时序图 | 见 `docs/doip_timing_diagram.md` |

## 快速开始（任务 1.1）

### 第 0 步：安装 Wireshark（必做，先于脚本）

任务 1.1 的目标是 **用 Wireshark 看包**，不是只跑通 Python 脚本。请先安装：

| 系统 | 做法 |
|------|------|
| Windows | [官网安装包](https://www.wireshark.org/download.html) + **Npcap**（含 Loopback 适配器） |
| Linux | `sudo apt install wireshark tshark`，用户加入 `wireshark` 组 |
| macOS | 官网 dmg + 按提示安装 **ChmodBPF** |

详细步骤、权限与自检：**[docs/wireshark_install.md](docs/wireshark_install.md)**

安装完成后：打开 Wireshark → 选 **Loopback (lo)** → 能抓到 `127.0.0.1` 流量再继续。

### 前置条件

- Wireshark 4.x（已安装且能抓回环网卡）
- Python 3.8+

### 第 1 步：开 Wireshark 并开始抓包

1. 选择 **Loopback: lo**（Windows 为 Npcap Loopback Adapter）
2. 点击开始抓包
3. 显示过滤器可先留空，抓完再用：`udp.port == 13400 || tcp.port == 13400`

### 第 2 步：终端 1 — 启动 DoIP 模拟 ECU

```bash
cd doip-learning/task1/scripts
python3 doip_udp_server.py
```

### 第 3 步：终端 2 — 启动 TCP 服务

```bash
cd doip-learning/task1/scripts
python3 doip_tcp_server.py
```

### 第 4 步：终端 3 — 运行客户端（触发完整流程）

```bash
cd doip-learning/task1/scripts
python3 doip_client.py --host 127.0.0.1
```

### Wireshark 抓包设置

1. 选择回环接口 `Loopback: lo`（Linux）或 `Adapter for loopback`（Windows）。
2. 开始抓包，再运行上面的客户端。
3. 推荐显示过滤器：

```
doip || (tcp.port == 13400) || (udp.port == 13400)
```

若 Wireshark 未识别 DoIP，用十六进制过滤器：

```
tcp.port == 13400 || udp.port == 13400
```

4. 在 TCP 流中应能看到 **SYN → SYN-ACK → ACK** 三次握手，随后才是 DoIP `0x0005` 路由激活。
5. 在 UDP 流中应只有 **单请求 → 单响应**，无握手。

详细分析步骤见 `docs/wireshark_guide.md`。

## 任务 1.1 附加练习：纯传输层对比

不依赖 DoIP 报文，先理解「为什么发现用 UDP、诊断用 TCP」：

```bash
cd doip-learning/task1/scripts
python3 tcp_udp_demo.py
```

Wireshark 过滤器：`tcp.port == 13402 or udp.port == 13401`

观察要点：

- **UDP**：一个数据包出去、一个回来，没有连接状态。
- **TCP**：必须先完成三次握手，再传应用数据，连接可长期保持（适合 UDS 会话和 Alive Check）。

## 任务 1.2：协议精读与时序图

**还没有 ISO 13400-2 PDF？** 先看 **[docs/iso13400_reading_guide.md](docs/iso13400_reading_guide.md)**（获取途径 + 章节阅读顺序 + 无 PDF 替代路径）。

1. 阅读 `docs/doip_message_format.md`（本仓库整理的 ISO 13400-2 要点）。
2. 对照 `docs/doip_timing_diagram.md` 中的 Mermaid 时序图，**手绘一版**并标注每步 Payload Type。
3. 自测：不看文档回答 README 末尾 5 道题。

## 本任务产出物

- [ ] Wireshark 截图：UDP 发现 + TCP 握手 + 路由激活 + 诊断报文
- [ ] 手绘 DoIP 完整时序图（发现 → 激活 → UDS → Alive Check）
- [ ] 能解释：为什么 0x0001 走 UDP、0x8001 走 TCP

## 自测题（任务 1 结束时应能脱口而出）

1. 车辆发现用 UDP 还是 TCP？为什么？
2. Routing Activation Request 必须包含什么信息？
3. UDS 的 0x27 安全访问在 DoIP 里如何封装传输？
4. 诊断仪连不上 ECU 时，排查顺序是什么？
5. Alive Check 机制解决什么问题？

参考答案提示见 `docs/self_check_answers.md`（先自己做，再对照）。

## 目录结构

```
task1/
├── README.md                 # 本文件
├── docs/
│   ├── iso13400_reading_guide.md  # 标准获取 + 精读章节顺序
│   ├── wireshark_install.md  # 安装 Wireshark（第 0 步）
│   ├── wireshark_guide.md    # 抓包逐步指南
│   ├── doip_message_format.md
│   ├── doip_timing_diagram.md
│   └── self_check_answers.md
└── scripts/
    ├── doip_common.py        # DoIP 报文构造
    ├── doip_udp_server.py    # UDP 发现服务
    ├── doip_tcp_server.py    # TCP 路由激活 + 诊断
    ├── doip_client.py        # 完整客户端流程
    └── tcp_udp_demo.py       # TCP vs UDP 对比 demo
```
