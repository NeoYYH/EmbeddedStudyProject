# 任务 1 自测参考答案

建议先独立完成 `README.md` 中的题目，再展开查看。

---

**1. 车辆发现用 UDP 还是 TCP？为什么？**

UDP。理由包括：发现阶段可能广播/多播，无需事先建立连接；单次请求-响应即可获取 VIN 与逻辑地址；无连接开销，适合快速扫描网段内多个 ECU；失败可短时超时重试而不影响已有 TCP 诊断连接。

---

**2. Routing Activation Request 必须包含什么信息？**

在 DoIP 头（含 Payload Type 0x0005）之后，payload 至少包含：**Source Address**（2 字节，测试仪逻辑地址）和 **Activation Type**（1 字节，常用 0x00 Default），以及标准规定的 Reserved / OEM 字段。ECU 用源地址将后续诊断报文路由到正确的 TCP 连接。

---

**3. UDS 的 0x27 安全访问在 DoIP 里如何封装传输？**

与 0x10、0x22 相同：放入 **Diagnostic Message（0x8001）** 的 User Data 字段，前面加上 2 字节 Source Address 和 2 字节 Target Address，整体经 **已激活的 TCP 连接** 发送。Seed/Key 交换的 UDS 语义不变，变的只是外层 DoIP 封装。

---

**4. 诊断仪连不上 ECU 时，排查顺序是什么？**

1. **物理层 / 链路**：网线/T1、PHY 链路 up、IP 是否同网段、能否 ping 通  
2. **端口与防火墙**：UDP/TCP 13400 是否可达  
3. **UDP 发现**：能否收到 0x0002（无响应则 IP/端口/ECU 未监听）  
4. **TCP 连接**：三次握手是否成功  
5. **路由激活**：0x0006 的 Response Code 是否为 0x10  
6. **DoIP/UDS 层**：Alive Check 超时、错误逻辑地址、NRC 等  

原则：**连不上先物理与 IP，连上但无诊断再查 DoIP 与 UDS**。

---

**5. Alive Check 机制解决什么问题？**

解决 **TCP 连接空闲时如何确认对端仍在线**。ECU 可周期性发 0x0007，测试仪须回 0x0008；超时未响应则 ECU 可关闭路由、释放资源，避免僵尸连接占满并发诊断槽位。对长时间空闲的 UDS 会话（如等车、等授权）尤为重要。
