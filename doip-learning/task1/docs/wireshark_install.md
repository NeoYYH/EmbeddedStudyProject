# Wireshark 安装指南（任务 1.1 第 0 步）

> **正确顺序**：先装 Wireshark → 再跑本仓库脚本 → 边抓包边对照分析。  
> 没有 Wireshark，任务 1.1 的核心练习（看 TCP 三次握手、对比 UDP 无连接）无法完成。

## 装哪个版本？

- 推荐安装 **最新稳定版**（4.x），自带 DoIP 协议解码（显示过滤器可用 `doip`）。
- 图形界面包名一般为 **Wireshark**；命令行抓包工具为 **tshark**（通常随 Wireshark 一起安装）。

官方下载页：https://www.wireshark.org/download.html

---

## Windows

1. 打开 https://www.wireshark.org/download.html ，下载 **Windows x64 Installer**。
2. 安装时勾选：
   - **Npcap**（必须，用于抓包；回环流量也依赖它）
   - 若提示安装 Npcap，选 *Install Npcap with WinPcap API-compatible Mode*
3. 首次启动若提示权限，选 **以管理员运行**（抓本机网卡时常需要）。
4. 验证：开始菜单打开 Wireshark，应能看到网卡列表（含 **Npcap Loopback Adapter**）。

抓本实验（127.0.0.1）时选 **Npcap Loopback Adapter**。

---

## Linux（Ubuntu / Debian）

```bash
sudo apt update
sudo apt install -y wireshark tshark

# 允许当前用户抓包（避免每次 sudo）
sudo dpkg-reconfigure wireshark-common
# 弹窗选 Yes：允许非 root 用户抓包

sudo usermod -aG wireshark $USER
# 注销并重新登录后生效
```

验证：

```bash
wireshark --version
tshark --version
```

抓本实验时选 **Loopback: lo**。

### Fedora / RHEL

```bash
sudo dnf install wireshark wireshark-cli
sudo usermod -aG wireshark $USER
```

---

## macOS

1. 下载 **macOS Intel 或 Apple Silicon** 对应 dmg：https://www.wireshark.org/download.html
2. 将 Wireshark 拖入 Applications，首次打开需在 **系统设置 → 隐私与安全性** 中允许。
3. 安装附带的 **ChmodBPF**（安装包内或官网说明），否则可能看不到网卡。
4. 抓本实验时选 **Loopback** 接口（若无，在 Capture Options 中勾选 *Enable loopback capture*，视版本而定）。

---

## 安装后 2 分钟自检

1. 打开 Wireshark，确认网卡列表非空。
2. 双击 **Loopback / lo** 开始抓包。
3. 浏览器访问 http://127.0.0.1 或 `ping 127.0.0.1`，应能看到回环流量。
4. 停止抓包 → 显示过滤器输入 `tcp` 或 `udp`，有结果即安装正常。

---

## 与本 DoIP 实验的配合

| 步骤 | 操作 |
|------|------|
| 0 | 按上文安装 Wireshark |
| 1 | 打开 Wireshark，选 Loopback，点开始抓包 |
| 2 | 运行 `doip_udp_server.py` + `doip_tcp_server.py` |
| 3 | 运行 `doip_client.py`，观察 UDP/TCP 报文 |
| 4 | 停止抓包，保存为 `task1_doip.pcapng` |

推荐过滤器：

```
udp.port == 13400 || tcp.port == 13400
```

若无 `doip` 解码列，用上面端口过滤器即可，手动看载荷是否以 `02 FD` 开头。

---

## 常见问题

**Q: 列表里没有 Loopback？**  
- Windows：确认 Npcap 已装，重装时勾选 loopback support。  
- Linux：用 `lo` 接口即可。  
- macOS：安装 ChmodBPF 或更新 Wireshark。

**Q: 提示没有权限抓包？**  
- Linux：加入 `wireshark` 组并重新登录。  
- Windows：以管理员运行 Wireshark。

**Q: 能不能不装 GUI，只用命令行？**  
可以，用 `tshark`：

```bash
sudo tshark -i lo -f "port 13400" -w task1_doip.pcapng
# 另一终端跑 client 后 Ctrl+C 停止，再用 wireshark task1_doip.pcapng 打开
```

任务 1.1 仍建议用 **图形界面**，便于第一次看清 TCP 握手和 Follow TCP Stream。
