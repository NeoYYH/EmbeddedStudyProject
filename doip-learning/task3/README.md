# 任务 3：异常场景与排障思维

> 对应学习计划第 3 周。在任务 2 已跑通正常 UDS 流程后，练习 **失败路径**。  
> **全部 7 个子任务总览** → 请看上级目录 [doip-learning/README.md](../README.md)

## 本阶段任务清单（仅任务 3）

| 编号 | 内容 | 脚本 / 文档 |
|------|------|-------------|
| 3.1 | 错误源地址、Alive Check、TCP 断连重连 | `scripts/doip_client_faults.py` |
| 3.2 | 对照真实 ECU 抓包 | 自备 `task1_doip.pcapng` + 公开样本 |
| 3.3 | 硬件层概念补充 | `docs/hardware_concepts.md` |

## 运行任务 3.1

先起服务（与任务 2 相同）：

```powershell
# 终端 1
cd doip-learning\task1\scripts
py doip_udp_server.py

# 终端 2
cd doip-learning\task2\scripts
py doip_tcp_server_uds.py

# 终端 3
cd doip-learning\task3\scripts
py doip_client_faults.py --host 127.0.0.1
```

## 任务 3.1 测什么

| 场景 | 期望 |
|------|------|
| 路由激活源地址 `0x1234`（非法） | Response Code **0x00** 拒绝 |
| Alive Check `0x0007` | 响应 `0x0008` + ECU 逻辑地址 |
| TCP 断开再连 | 重新激活后可再发 UDS `10 01` |

## 任务 3.2 / 3.3

- **3.2**：对比你的 pcap 与公开 DoIP 样本，写 3 条相同点 + 2 条差异  
- **3.3**：阅读 [hardware_concepts.md](docs/hardware_concepts.md)（100BASE-T1、PHY、排障顺序）

## 完成标准

- [ ] `doip_client_faults.py` 全部 PASS  
- [ ] 能解释路由激活码 `0x00` vs `0x10`  
- [ ] 完成 3.2 抓包对比笔记  
- [ ] 完成 3.3 硬件概念阅读  
