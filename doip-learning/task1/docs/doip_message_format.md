# ISO 13400-2 DoIP 报文格式要点（任务 1.2 精读笔记）

> 正式学习请以 ISO 13400-2 标准原文为准；本文为任务导向速查。

## 通用报文头（所有 Payload 共有）

| 字节偏移 | 长度 | 字段 | 说明 |
|----------|------|------|------|
| 0 | 1 | Protocol Version | 常用 `0x02`（2012 版） |
| 1 | 1 | Inverse Protocol Version | 必须为 `0xFF - Version`，即 `0xFD` |
| 2 | 2 | Payload Type | 大端，见下表 |
| 4 | 4 | Payload Length | 大端，仅 payload 长度，不含头 8 字节 |

**合法性检查**：Version 与 Inverse Version 之和应为 `0xFF`。Wireshark 中首先找 `02 FD` 可快速定位 DoIP 帧。

## 任务 1 必记 Payload Type

| Type | 名称 | 传输 | 任务优先级 |
|------|------|------|------------|
| 0x0001 | Vehicle Identification Request | UDP | 必会 |
| 0x0002 | Vehicle Identification Response | UDP | 必会 |
| 0x0005 | Routing Activation Request | TCP | 必会 |
| 0x0006 | Routing Activation Response | TCP | 必会 |
| 0x8001 | Diagnostic Message | TCP | 必会 |
| 0x8002 | Diagnostic Message Positive Ack | TCP | 必会 |
| 0x8003 | Diagnostic Message Negative Ack | TCP | 了解 |
| 0x0007 | Alive Check Request | TCP | 必会 |
| 0x0008 | Alive Check Response | TCP | 必会 |

## 各 Payload 结构摘要

### 0x0001 Vehicle Identification Request

- Payload Length = **0**（无 body）

### 0x0002 Vehicle Identification Response

| 字段 | 长度 |
|------|------|
| VIN | 17 |
| Logical Address | 2 |
| EID | 6 |
| GID | 6 |
| Further Action Required | 1 |

### 0x0005 Routing Activation Request

| 字段 | 长度 |
|------|------|
| Source Address | 2 |
| Activation Type | 1 |
| Reserved | 4 |
| OEM Specific | 4（可选，标准中常为 4 字节） |

### 0x0006 Routing Activation Response

| 字段 | 长度 |
|------|------|
| Client Logical Address | 2 |
| Logical Address（ECU） | 2 |
| Response Code | 1 |
| OEM Specific | 4 |

**常见 Response Code**：

| 值 | 含义 |
|----|------|
| 0x10 | 成功，路由已激活 |
| 0x00–0x0F | 各类拒绝原因（未知源地址、已达最大连接数等） |

### 0x8001 Diagnostic Message

| 字段 | 长度 |
|------|------|
| Source Address | 2 |
| Target Address | 2 |
| User Data | N（**UDS 数据在此**） |

示例：UDS 安全访问 `27 01` 完整 DoIP 帧结构为：

```
[DoIP Header 8B][Src 2B][Tgt 2B][27 01...]
```

### 0x8002 / 0x8003 诊断确认

含源/目标地址 + Ack Code；否定确认含错误原因码。

### 0x0007 / 0x0008 Alive Check

- Request：无 payload
- Response：2 字节 Source Address（ECU 逻辑地址）

## 端口与传输

- **IANA 端口 13400**：UDP 与 TCP 均使用（发现用 UDP，已建立连接后的控制与诊断用 TCP）。
- 车辆发现也可使用 **UDP 13400 广播**到网段。

## 精读 ISO 13400-2 时的阅读顺序建议

1. 第 7 章：DoIP 报文通用格式
2. 车辆发现（Vehicle discovery）
3. 路由激活（Routing activation）
4. 诊断报文传输（Diagnostic message）
5. 连接管理 / Alive Check

跳读建议：实体管理、边缘节点等章节可第 3 周再补。

## 与 AUTOSAR 模块对应

| 标准概念 | AUTOSAR 模块 |
|----------|--------------|
| DoIP 报文编解码 | DoIP |
| Socket / TCP / UDP | SoAd + TcpIp |
| UDS 服务 | Dcm（与 CAN 相同） |

任务 1 只需建立「标准报文 ↔ Wireshark 字节」映射，BSW 配置留到具体 MCU 项目。
