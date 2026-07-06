# DoIP 以太网诊断学习计划 — 总览

> **背景**：已有 CAN UDS（ISO 14229）经验，目标掌握 DoIP（ISO 13400），完成 CAN → 以太网诊断知识迁移。  
> **场景**：智能车灯（矩阵 LED / ADB）、Cypress/Infineon Traveo II 等车规 MCU 平台。  
> **核心结论**：UDS 应用层完全复用，学习重点在 **DoIP 传输/会话层**。

---

## 任务总览：一共 7 个子任务

| 周次 | 编号 | 任务名称 | 类型 | 对应目录 |
|------|------|----------|------|----------|
| 第 1 周 | **1.1** | Wireshark 抓包 + TCP/UDP 对比 | 动手 + 抓包 | [task1/](task1/README.md) |
| 第 1 周 | **1.2** | 精读 ISO 13400-2 + 手绘时序图 | 文档 + 理论 | [task1/docs/](task1/docs/) |
| 第 2 周 | **2.1** | 搭建 DoIP 模拟器（UDP 发现 + TCP 激活） | 动手 | [task1/scripts/](task1/scripts/) + [task2/scripts/](task2/scripts/) |
| 第 2 周 | **2.2** | 接入 UDS：0x10 / 0x22 / NRC | 动手 + 代码 | [task2/](task2/README.md) |
| 第 3 周 | **3.1** | 异常场景：错误地址 / Alive Check / 断连重连 | 动手 | [task3/](task3/README.md) |
| 第 3 周 | **3.2** | 对照真实 ECU 抓包与模拟器差异 | 分析 | 自备 pcap |
| 第 3 周 | **3.3** | 硬件层概念补充（100BASE-T1 / PHY） | 阅读 | [task3/docs/hardware_concepts.md](task3/docs/hardware_concepts.md) |

**统计**：3 个大阶段（任务 1 / 2 / 3）→ **7 个子任务**（1.1、1.2、2.1、2.2、3.1、3.2、3.3）

---

## 进度总表（可打勾）

| 编号 | 任务 | 状态 |
|------|------|------|
| 1.1 | Wireshark 抓包实践 | ⬜ |
| 1.2 | ISO 13400-2 精读 + 时序图 | ⬜ |
| 2.1 | DoIP 模拟器搭建 | ⬜ |
| 2.2 | UDS 0x10 / 0x22 / NRC | ⬜ |
| 3.1 | 异常场景演练 | ⬜ |
| 3.2 | 真实抓包对照分析 | ⬜ |
| 3.3 | 硬件层概念阅读 | ⬜ |

---

## 一键跑全部可执行任务（1.1 / 2.1 / 2.2 / 3.1）

以下子任务有自动化脚本，可一条命令串跑：

```powershell
cd doip-learning
py run_all_tasks.py
```

或双击 `run_all_tasks.bat`。成功标志：**`ALL TASKS PASSED`**。

| 脚本覆盖 | 未覆盖（需手动完成） |
|----------|-------------------|
| 1.1 抓包流程、2.1 模拟器、2.2 UDS、3.1 异常 | 1.2 文档精读、3.2 抓包分析、3.3 硬件阅读 |

---

# 第 1 周：DoIP 基础 + 协议文档

## 任务 1.1 — Wireshark 抓包：TCP 三次握手 vs UDP 无连接

**目标**：理解 DoIP 为何用 UDP 做发现、TCP 做数据传输。

### 前置（第 0 步）

- [ ] 安装 Wireshark + Npcap（Windows）
- [ ] 能抓 **Adapter for loopback traffic capture** 回环流量
- [ ] 本机安装 Python，代码在 **Windows PowerShell** 跑（不是 Cursor 云端终端）

详见：[task1/docs/wireshark_install.md](task1/docs/wireshark_install.md)

### 操作步骤

| 步骤 | 操作 |
|------|------|
| 1 | Wireshark 选回环网卡，开始抓包 |
| 2 | 终端 1：`task1/scripts/doip_udp_server.py` |
| 3 | 终端 2：`task1/scripts/doip_tcp_server.py` |
| 4 | 终端 3：`task1/scripts/doip_client.py --host 127.0.0.1` |
| 5 | 过滤器：`udp.port == 13400 \|\| tcp.port == 13400` |
| 6 | 保存 `task1_doip.pcapng` |

### 附加练习

```powershell
cd task1\scripts
py tcp_udp_demo.py
```

过滤器：`tcp.port == 13402 or udp.port == 13401`

### 产出物

- [ ] Wireshark 截图或 pcap 文件
- [ ] 能指出：TCP 握手、0x0001、0x0005、0x8001 各是哪几条包
- [ ] 能解释：发现为何 UDP、诊断为何 TCP

### 参考文档

- [wireshark_guide.md](task1/docs/wireshark_guide.md)

---

## 任务 1.2 — 精读 ISO 13400-2 + 手绘 DoIP 时序图

**目标**：建立「标准报文 ↔ Wireshark 字节」映射。

### 阅读顺序

1. [iso13400_reading_guide.md](task1/docs/iso13400_reading_guide.md) — 标准获取 + 章节顺序
2. [doip_message_format.md](task1/docs/doip_message_format.md) — 报文格式速查
3. [doip_timing_diagram.md](task1/docs/doip_timing_diagram.md) — 时序图模板
4. 对照 `task1_doip.pcapng` 逐字段核对

### 产出物

- [ ] 手绘完整时序图（发现 → 激活 → UDS → Alive Check），标注 Payload Type
- [ ] 完成下方 5 道自测题（先自己做，再对答案）

### 自测题

1. 车辆发现用 UDP 还是 TCP？为什么？
2. Routing Activation Request 必须包含什么信息？
3. UDS 0x27 安全访问在 DoIP 里如何封装？
4. 诊断仪连不上 ECU 的排查顺序？
5. Alive Check 解决什么问题？

答案：[self_check_answers.md](task1/docs/self_check_answers.md)

---

# 第 2 周：动手实践 — DoIP 模拟器 + UDS

## 任务 2.1 — 搭建最简 DoIP 模拟器

**目标**：UDP 处理发现，TCP 处理路由激活，Wireshark 验证报文格式。

| 组件 | 脚本 | 说明 |
|------|------|------|
| UDP Server | `task1/scripts/doip_udp_server.py` | 0x0001 → 0x0002 |
| TCP Server | `task2/scripts/doip_tcp_server_uds.py` | 0x0005 → 0x0006 |
| 公共报文库 | `task1/scripts/doip_common.py` | DoIP 头与构造 |

### 验证

- [ ] 终端见 `Listening on 0.0.0.0:13400`
- [ ] Wireshark 可见完整 DoIP 头 `02 FD`

---

## 任务 2.2 — 接入 UDS：0x10 / 0x22 / NRC

**目标**：跑通「发现 → 激活 → UDS 会话」全流程，验证 UDS 与 CAN 一致。

### 运行

```powershell
# 终端 1
cd task1\scripts & py doip_udp_server.py

# 终端 2
cd task2\scripts & py doip_tcp_server_uds.py

# 终端 3
cd task2\scripts & py doip_client_uds.py --host 127.0.0.1
```

### 自动测试用例

| 步骤 | UDS 请求 | 期望 |
|------|----------|------|
| 1 | `10 01` | `50 01` 默认会话 |
| 2 | `22 F1 90` | `62 F1 90` + VIN |
| 3 | `22 F1 86` | `62 F1 86` 当前会话 |
| 4 | `22 F1 87` | **NRC 7F 22 22**（默认会话不可读） |
| 5 | `10 03` | `50 03` 扩展会话 |
| 6 | `22 F1 87` | `62 F1 87` 零件号 |
| 7 | `22 FF FF` | **NRC 7F 22 31** 未知 DID |
| 8 | `99 00` | **NRC 7F 99 11** 服务不支持 |

### 内置 DID（模拟车灯 ECU）

| DID | 含义 | 条件 |
|-----|------|------|
| F190 | VIN | 默认会话 |
| F186 | 当前会话 | 默认会话 |
| F187 | 零件号 | 仅扩展会话 0x03 |

### 产出物

- [ ] 理解 DoIP 层：`0x8001` 请求 → `0x8002` Ack → `0x8001` UDS 响应
- [ ] Wireshark 中找到 `7F 22 31` 并解释
- [ ] 能改 `uds_ecu.py` 新增一个 DID

---

# 第 3 周：进阶与排障

## 任务 3.1 — 异常场景演练

**目标**：练习失败路径，建立排障直觉。

```powershell
cd task3\scripts
py doip_client_faults.py --host 127.0.0.1
```

| 场景 | 期望 |
|------|------|
| 路由激活源地址 `0x1234`（非法） | Response Code **0x00** |
| Alive Check `0x0007` | 响应 `0x0008` |
| TCP 断开再连 | 重新激活后可再发 `10 01` |

### 产出物

- [ ] 三种异常场景均 PASS
- [ ] 能解释 0x00 与 0x10 路由激活码区别

---

## 任务 3.2 — 对照公开 DoIP 抓包样本

**目标**：对比真实 ECU 与自建模拟器差异。

### 操作

1. 打开你的 `task1_doip.pcapng`
2. 搜索公开样本（如 CANoe 演示、GitHub doip pcap）
3. 对比：Payload Type、时序、Ack 是否分帧、VIN 字段

### 产出物

- [ ] 列出至少 3 处「模拟器 vs 实车」相同点
- [ ] 列出至少 2 处差异及可能原因

---

## 任务 3.3 — 硬件层概念补充（半天阅读）

**目标**：建立物理层直觉，不深入实操。

阅读：[task3/docs/hardware_concepts.md](task3/docs/hardware_concepts.md)

要点：

- 100BASE-T1 单对双绞线
- PHY 链路自协商，失败 = 完全连不上
- 排障顺序：物理层 → IP → UDP 发现 → TCP → DoIP → UDS

### 产出物

- [ ] 能说出 AUTOSAR 分层：Dcm → DoIP → SoAd → TcpIp → EthIf → Eth

---

# 知识速查：CAN UDS → DoIP 变与不变

| 层级 | 是否变化 | 说明 |
|------|----------|------|
| UDS 服务（0x10/0x22/0x27…） | ✅ 不变 | 直接迁移 |
| 会话状态机、NRC | ✅ 不变 | 直接迁移 |
| 传输层 | ❌ 变化 | CAN + ISO-TP → DoIP + TCP/UDP |
| 物理层 | ❌ 变化 | CAN 总线 → 100BASE-T1 等 |

---

# DoIP 必记 Payload Type

| Type | 名称 | 传输 |
|------|------|------|
| 0x0001 | Vehicle Identification Request | UDP |
| 0x0002 | Vehicle Identification Response | UDP |
| 0x0005 | Routing Activation Request | TCP |
| 0x0006 | Routing Activation Response | TCP |
| 0x8001 | Diagnostic Message | TCP |
| 0x8002 | Diagnostic Positive Ack | TCP |
| 0x8003 | Diagnostic Negative Ack | TCP |
| 0x0007 | Alive Check Request | TCP |
| 0x0008 | Alive Check Response | TCP |

---

# 推荐学习顺序（时间线）

```
第 1 周
  Day 1-2   任务 1.1  装 Wireshark + 抓包 + 保存 pcap
  Day 3-4   任务 1.2  读协议文档 + 手绘时序图 + 5 道自测
  Day 5     复习 + 过一遍 self_check_answers

第 2 周
  Day 1     任务 2.1  跑通模拟器，Wireshark 再验证
  Day 2-4   任务 2.2  跑 UDS 客户端，读 uds_ecu.py，试改 DID
  Day 5     自测：能口述 DoIP 三层时序 + UDS 封装

第 3 周
  Day 1-2   任务 3.1  异常场景脚本 + Wireshark
  Day 3     任务 3.2  对比真实抓包
  Day 4     任务 3.3  硬件概念阅读
  Day 5     全流程复盘：run_all_tasks.py + 口头讲解
```

---

# 仓库目录索引

```
doip-learning/
├── README.md                 ← 本文件（全部任务总览）
├── run_all_tasks.py          ← 一键跑任务 1+2+3 脚本部分
├── run_all_tasks.bat
├── task1/                    ← 第 1 周（仅任务 1 详情）
│   ├── README.md
│   ├── docs/
│   └── scripts/
├── task2/                    ← 第 2 周（仅任务 2 详情）
│   ├── README.md
│   └── scripts/
└── task3/                    ← 第 3 周（仅任务 3 详情）
    ├── README.md
    ├── docs/
    └── scripts/
```

---

# 全部完成标准

完成 **7 个子任务** 后，你应能：

1. 不看文档画出 DoIP 完整时序图  
2. 用 Wireshark 从 pcap 指出各 Payload Type  
3. 解释 UDP/TCP 分工及排障顺序  
4. 说明 UDS 在 `0x8001` 中如何封装（含 0x27）  
5. 独立跑通模拟器并完成 0x10 / 0x22 与 NRC 测试  
6. 处理错误源地址、Alive Check、断连重连场景  
7. 对 100BASE-T1 / PHY 有概念级认知  

---

*最后更新：与仓库 task1 / task2 / task3 脚本同步。*
