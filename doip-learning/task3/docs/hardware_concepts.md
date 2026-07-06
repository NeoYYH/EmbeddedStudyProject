# 硬件层概念补充（任务 3.3，仅浏览）

任务 1–2 在应用层/协议层完成学习即可。接真实 ECU 前需建立以下概念：

## 100BASE-T1 单对以太网

- 车用以太网常用 **单对双绞线（T1）**，不是家用 RJ45 八线
- 诊断仪与 ECU 之间可能是 **媒体转换器** 或 **车载以太网 USB 适配器**

## PHY 与链路

- **PHY** 负责物理层：链路 up/down、自协商
- 链路 down 时：ping 不通、TCP 连不上 — **不是 DoIP 协议报错**
- 排障：**先确认 Link LED / 链路状态**

## AUTOSAR 栈（概念）

```
Dcm (UDS) → DoIP → SoAd → TcpIp → EthIf → Eth → MAC/PHY
```

任务 3 只需知道「DoIP 在 Dcm 下面、TCP 上面」；具体 BSW 配置绑定 Traveo II 等项目时再学。

## 与 DoIP 排障顺序

1. 网线 / T1 / PHY 链路
2. IP 同网段、ping
3. UDP 13400 发现
4. TCP 握手 + 路由激活 0x10
5. UDS / NRC
