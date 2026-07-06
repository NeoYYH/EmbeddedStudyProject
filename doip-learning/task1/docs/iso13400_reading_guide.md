# ISO 13400-2 获取方式 + 精读阅读顺序（任务 1.2）

> 你说得对：**得先有可读材料，才能精读。**  
> 本文分两条路：**有标准 PDF** 时怎么读；**暂时没有 PDF** 时用什么替代、读到什么程度。

---

## 一、标准文档怎么获取？

ISO 13400-2 是**付费标准**，没有合法的完整免费 PDF。可选途径：

### 途径 1：公司/学校资源（优先试这个）

- 问部门同事、测试台架供应商、诊断工具厂商（CANoe、DTS 等）是否已有库
- 公司标准资料库、高校图书馆数据库
- 很多车企 Tier1 内部有 **ISO 13400-2:2019** 或 **:2012** 存档

### 途径 2：官方购买

| 版本 | 说明 | 购买入口 |
|------|------|----------|
| **ISO 13400-2:2019** | 行业引用最多，协议版本 **0x02**，**学习任务 1 推荐买这版** | https://www.iso.org/standard/75094.html |
| ISO 13400-2:2012 | 第一版，老项目可能仍引用 | https://www.iso.org/standard/55283.html |
| ISO 13400-2:2025 | 2025-06 最新第三版，含 TLS 等更新 | https://www.iso.org/standard/13400-2 |

国内也可通过 **全国标准信息公共服务平台** 查 ISO 采标情况，或通过 BSI、SAC 授权渠道购买。

### 途径 3：免费预览（只能看目录/前几页，不能替代精读）

- ISO 官网部分页面有 **Preview**（通常只有 Scope、目录）
- https://standards.iteh.ai 可搜 `ISO 13400-2`，有 **Document Preview**（目录 + 片段），够你确认章节号，**不够做任务 1.2 全文精读**

### 买哪个版本？

| 你的情况 | 建议 |
|----------|------|
| 只为学习任务 1–2 周 | **2019 版** 足够（与实验脚本 `02 FD` 头一致） |
| 公司项目指定 2025 | 跟项目版本 |
| 暂时买不起 | 走下文 **「无 PDF 替代阅读路径」**，结合本仓库笔记 + 你的 `task1_doip.pcapng` |

---

## 二、有 PDF 时的精读顺序（按章节号）

下面按 **ISO 13400-2:2019 / 2025** 常见结构排列（两版章节号基本一致，以你 PDF 目录为准微调）。

### 第 1 遍：建立全局（约 30 分钟，先不抠字节）

| 顺序 | 章节 | 读什么 | 目的 |
|------|------|--------|------|
| 0 | **Scope（范围）** + **Introduction** | 标准管什么、不管什么 | 知道 DoIP 只管传输/发现/路由，UDS 在 ISO 14229 |
| 1 | **第 6 章** Connection establishment and vehicle discovery | 连接建立与发现总览 | 建立「先发现、再 TCP、再激活」直觉 |
| 2 | **6.3 Vehicle network integration**（浏览） | IP 分配、多车同网 | 概念即可，任务 1 不深入 |

### 第 2 遍：报文格式（核心，对照 Wireshark）

| 顺序 | 章节 | 读什么 | 对照你的 pcap |
|------|------|--------|---------------|
| 3 | **第 7 章 APP** — **7.2 Data transmission order** | 字节序、大端 | 所有多字节字段与抓包一致 |
| 4 | **第 9 章 Service interface** — **9.1~9.2**（若有） | 服务原语概览 | 可快读 |
| 5 | **9.3 AL – Handling of UDP packets and TCP data** | UDP/TCP 分工 | 为何 0x0001 走 UDP、0x8001 走 TCP |
| 6 | **9.4 AL – Supported payload types** | **Payload Type 全表** | 背任务 1 九种 type |
| 7 | **7.4 APP – Vehicle identification and announcement** | 0x0001 / 0x0002 字段定义 | 对照 pcap 里 VIN、`0x0E00` |
| 8 | **9.5 AL – Diagnostic message and acknowledgement** | 0x8001 / 0x8002 / 0x8003 | 对照 UDS `10 01` 封装 |
| 9 | **6.2 / 7.10 / 9.x 中 Routing activation 相关小节** | 0x0005 / 0x0006、Response Code | 对照 `0x10` 成功码 |
| 10 | **9.6 AL – Alive check** | 0x0007 / 0x0008 | 任务 1.2 时序图最后一环 |
| 11 | **7.7 Timing and communication parameters** | 超时、重试 | 第 3 周排障用，先标重点 |

### 第 3 遍：任务导向查漏（约 1 小时）

| 顺序 | 章节 | 动作 |
|------|------|------|
| 12 | **7.8 Logical address assignment** | 理解测试仪 `0x0E80`、ECU `0x0E00` 从哪来 |
| 13 | **9.8 Status message**（若有） | 了解即可 |
| 14 | **第 10 章 TLS** | **任务 1 跳过** |
| 15 | **第 11 章及以后** 实体管理、边缘节点 | **任务 1 跳过**，第 3 周再读 |

### 阅读时固定动作（每读完一节）

1. 在 PDF 里标出 **Payload Type 十六进制**
2. 打开 `task1_doip.pcapng`，过滤器 `udp.port == 13400 || tcp.port == 13400`
3. 找到对应包，核对 **字段长度与顺序**
4. 在 `doip_timing_diagram.md` 手绘图上补一笔

---

## 三、暂时没有 PDF 时的替代阅读路径（可立刻开始）

按下面顺序读 **本仓库免费材料**，效果约等于标准第 7、9 章核心：

| 顺序 | 材料 | 路径 | 对应标准章节 |
|------|------|------|--------------|
| 1 | 报文格式速查 | `docs/doip_message_format.md` | 9.4、7.4、9.5、9.6 |
| 2 | 你的抓包 + 分析结论 | `task1_doip.pcapng` + 任务 1.1 对话记录 | 实机验证 |
| 3 | Wireshark 逐步对照 | `docs/wireshark_guide.md` | 9.3 |
| 4 | 时序图模板 | `docs/doip_timing_diagram.md` | 第 6、7 章流程 |
| 5 | 自测题 | `README.md` + `docs/self_check_answers.md` | 检验是否读懂 |

**公开补充资料（免费）：**

- AUTOSAR_SWS_DiagnosticOverIP（搜 AUTOSAR DoIP SWS PDF，与 ISO 13400 高度对齐）
- Wireshark 内置 DoIP 解码器：Help → Protocols → DOIP
- ISO 官网 Scope 页：https://www.iso.org/standard/75094.html （确认标准边界）

---

## 四、任务 1.2 最小精读清单（无论有没有 PDF）

读完应能在纸上画出并标注：

```
UDP  0x0001 → 0x0002
TCP  SYN×3 → 0x0005 → 0x0006(0x10)
TCP  0x8001[UDS] → 0x8002 → 0x8001[UDS响应]
TCP  0x0007 → 0x0008（Alive Check）
```

并能填写：

| Payload | 传输 | Payload 里最关键字段 |
|---------|------|----------------------|
| 0x0001 | UDP | 无 body |
| 0x0002 | UDP | VIN(17) + Logical Address(2) + … |
| 0x0005 | TCP | Source Address + Activation Type |
| 0x0006 | TCP | Response Code（0x10=成功） |
| 0x8001 | TCP | Src/Tgt Address + **UDS 数据** |
| 0x8002 | TCP | Ack |
| 0x0007/0x0008 | TCP | 保活 |

---

## 五、建议你这周的具体安排

| 天 | 有 PDF | 无 PDF |
|----|--------|--------|
| Day 1 | 买/借 2019 版 + 读 Scope + 第 6 章 | 读 `doip_message_format.md` 全文 |
| Day 2 | 9.3 + 9.4 + 7.4 | 对照 pcap 逐字段标注 |
| Day 3 | 9.5 + Routing Activation + 9.6 | 手绘 `doip_timing_diagram.md` |
| Day 4 | 7.7 计时参数浏览 | 做 5 道自测题 |
| Day 5 | 查漏补缺 | 向公司要 PDF，用本文第二节重读一遍 |

---

## 六、ISO 13400 系列关系（避免下错单）

| 部分 | 内容 | 任务 1 是否需要 |
|------|------|----------------|
| ISO 13400-1 | 一般信息和用例定义 | 可选浏览 |
| **ISO 13400-2** | **传输协议与网络层（你要的）** | **必买/必读** |
| ISO 13400-3 | 有线链路（100BASE-T1 等） | 第 3 周硬件概念 |
| ISO 13400-4 | 以太网诊断接口 | 接实车时再读 |

**只买一本的话，买 Part 2。**
