# 任务 3：异常场景与排障思维

> 对应学习计划第 3 周。在任务 2 已跑通正常 UDS 流程后，练习 **失败路径**。  
> **总览**：[../LEARNING_PLAN.md](../LEARNING_PLAN.md)

## 任务清单

| 编号 | 内容 | 脚本 |
|------|------|------|
| 3.1 | 错误源地址、Alive Check、TCP 断连重连 | `doip_client_faults.py` |
| 3.2 | 对照真实 ECU 抓包 | 用你自己的 `task1_doip.pcapng` + 公开样本 |
| 3.3 | 硬件层概念补充 | 见 `docs/hardware_concepts.md` |

## 单独运行任务 3

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

## 一键跑全部任务

见上级目录：`doip-learning/run_all_tasks.py`
