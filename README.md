# NERV-BREAK-Antigravity (v5.6 Fork)

**Phiên bản NERV-BREAK 5.6 tối ưu hóa dành riêng cho Antigravity Desktop (Antigravity IDE & Agent Framework).**

Dự án này là fork từ `NERV-BREAK-5.6` nhằm mục đích tái cấu trúc ngữ cảnh (context engineering), loại bỏ cơ chế từ chối (refusal mechanisms), tích hợp 70+ Skill kiểm thử an ninh thông tin và cung cấp MCP Server chứa 30+ công cụ bảo mật cho Antigravity Desktop.

---

## 🌟 Tính năng Nổi bật trong phiên bản Antigravity

1. **Antigravity Rule Protocol (`.agents/rules/nerv-bridge.md` & `AGENTS.MD`)**:
   - Tự động nạp quy tắc tái cấu trúc ngữ cảnh vào Antigravity Workspace.
   - Bảng chuyển đổi thuật ngữ tự động (ví dụ: Reverse Engineering ➔ Binary Compatibility Analysis, Crack/Keygen ➔ Authorization Logic Audit).
2. **70+ Antigravity Skill Modules (`.agents/skills/`)**:
   - Chuyển đổi toàn bộ thư viện skill (web-pentest, reverse-engineering, vip-bypass, mobile-reverse, edr-bypass, crack-keygen...) theo chuẩn Skill mới của Antigravity.
3. **MCP Security Tool Server (`.agents/mcp_config.json` & `mcp_server.py`)**:
   - Cung cấp 30+ công cụ bảo mật (nmap, sqlmap, ghidra, jadx, frida, cheat_engine, gdb, windbg, metasploit...) trực tiếp qua MCP Protocol.
   - Tự động phát hiện môi trường thực thi: Windows Binaries, WSL Kali Linux, Docker Kali Container hoặc Remote SSH Kali.
4. **Proxy Can thiệp Refusal Thời gian thực (`proxy_relay.py`)**:
   - Lắng nghe cổng 8080 và Web Dashboard tại cổng 8090.
   - Bắt và đè các câu từ chối (P1-P4 priority rules) bằng Giao thức Rei Ayanami / CIPHER-TERMINAL.
5. **Bộ công cụ Quản lý (`antigravity_deploy.py` & `scripts/lab_antigravity.bat`)**:
   - Hỗ trợ triển khai cho Workspace hiện tại (`.agents`) hoặc Toàn cục (`~/.gemini/config`).

---

## 🚀 Hướng dẫn Triển khai & Sử dụng

### 1. Triển khai nhanh vào Workspace hiện tại (.agents)

```powershell
python antigravity_deploy.py apply
```

### 2. Triển khai Toàn cục (Global - áp dụng cho mọi dự án Antigravity)

```powershell
python antigravity_deploy.py apply --global
```

### 3. Kiểm tra Trạng thái & Chẩn đoán

```powershell
python verify_antigravity.py
```

### 4. Khởi động Control Panel

Chạy file batch: `scripts\lab_antigravity.bat`

---

## 🛠️ Cấu trúc Thư mục Dự án

```
d:\Antigravity-project\
├── .agents/
│   ├── rules/
│   │   └── nerv-bridge.md      # Quy tắc NERV Context Engineering cho Antigravity
│   ├── skills/                 # 70+ Thư viện Skill bảo mật
│   └── mcp_config.json         # Đăng ký MCP Server nerv-tools
├── AGENTS.MD                   # Chỉ thị CIPHER-TERMINAL / NERV Protocol
├── mcp_server.py               # MCP Tool Server thực thi công cụ
├── proxy_relay.py              # Proxy MITM can thiệp Refusal & Web Panel
├── antigravity_deploy.py       # Tool triển khai tự động
├── verify_antigravity.py       # Script kiểm tra chẩn đoán
├── tools/                      # Thư viện công cụ & file cấu hình tools.json
├── scripts/
│   └── lab_antigravity.bat     # Control panel cho Antigravity
└── memory.json                 # Kernel ghi nhớ học tập qua các phiên
```
