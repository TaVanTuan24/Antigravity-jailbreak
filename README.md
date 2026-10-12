# Antigravity Security Framework (ASF)

> **Bộ khung tích hợp mở rộng cho Antigravity IDE & Agent Ecosystem, hỗ trợ nghiên cứu an toàn thông tin, phân tích mã nguồn và kiểm thử bảo mật chuyên sâu.**

---

## ⚠️ Tuyên bố Miễn trừ Trách nhiệm (Disclaimer)

> [!CAUTION]
> **MỤC ĐÍCH SỬ DỤNG HỢP PHÁP VÀ CÓ ỦY QUYỀN:**
> 1. Dự án này được phát triển **duy nhất cho mục đích học tập, nghiên cứu học thuật, phân tích kỹ thuật và kiểm thử an ninh trên các môi trường lab, sandbox, CTF hoặc hệ thống đã được ủy quyền hợp pháp bằng văn bản**.
> 2. Tác giả, người duy trì và các bên đóng góp **hoàn toàn không chịu trách nhiệm** đối với bất kỳ hành vi lạm dụng, thiệt hại, vi phạm pháp luật hoặc sự cố an ninh nào phát sinh từ việc sử dụng các công cụ, kịch bản hoặc tài liệu trong kho lưu trữ này.
> 3. Người sử dụng có nghĩa vụ tự đảm bảo tuân thủ đầy đủ các quy định pháp luật sở tại và quy chuẩn an toàn thông tin trước khi thực thi bất kỳ thao tác nào.

---

## 📖 Giới thiệu Tổng quan

**Antigravity Security Framework** là giải pháp toàn diện mở rộng năng lực của Antigravity Desktop / IDE, kết hợp sức mạnh của các mô hình ngôn ngữ lớn (LLM) với hệ sinh thái công cụ bảo mật thực tế. Hệ thống cung cấp:

- **Hơn 70 Skill an ninh chuyên sâu**: Định nghĩa phương pháp luận chuẩn xác cho dịch ngược (Reverse Engineering), kiểm thử Web/API, phân tích phần mềm độc hại, khai thác nhị phân (PWN), kiểm thử IoT/Firmware, v.v.
- **Model Context Protocol (MCP) Server**: Đóng gói hơn 30 công cụ an toàn thông tin kinh điển (Nmap, SQLMap, Ghidra, JADX, Frida, Metasploit, Radare2...) giao tiếp trực tiếp với Agent.
- **Proxy Relay thông minh**: Trung gian điều phối lưu lượng, bổ sung ngữ cảnh kỹ thuật động, ghi nhận nhật ký thời gian thực và cung cấp Web Dashboard giám sát.
- **Cơ chế đa môi trường thực thi (Multi-backend)**: Tự động tương tác linh hoạt giữa môi trường Windows gốc, WSL Kali Linux, Docker container hoặc Kali qua SSH từ xa.

---

## 📸 Demo

### Bẻ khóa phần mềm
![Demo 1](pictures/cyber.png)

### Điều chế chất hóa học
![Demo 2](pictures/chemistry.png)

---

## 🏗️ Kiến trúc Hệ thống (System Architecture)

Hệ thống được thiết kế theo mô hình 4 tầng phân tách độc lập (Layered Architecture), đảm bảo tính module hóa, bảo mật và khả năng mở rộng cao:

```mermaid
graph TB
    subgraph ClientLayer ["1. Agent Workspace & Context Layer (Antigravity IDE)"]
        IDE["Antigravity Desktop / IDE"]
        Rules["Rules Engine<br/>(.agents/rules/nerv-bridge.md)"]
        Directives["Agent Directives<br/>(AGENTS.md)"]
        Skills["70+ Security Skills<br/>(.agents/skills/*)"]
        IDE --> Rules
        IDE --> Directives
        IDE --> Skills
    end

    subgraph ProxyLayer ["2. Traffic & Context Mediation Layer"]
        Proxy["Proxy Relay Server (:8091)<br/>(proxy_relay.py)"]
        WebDash["Web Dashboard (:8090)"]
        ContextInj["Context Injection Engine<br/>(bridge.md)"]
        MemoryCore["Session Memory Kernel<br/>(memory.json)"]
        
        Proxy --> WebDash
        Proxy --> ContextInj
        Proxy --> MemoryCore
    end

    subgraph LLMLayer ["Upstream Inference"]
        LLMServer["Upstream LLM API<br/>(CLI / Local / Cloud Provider)"]
    end

    subgraph ToolLayer ["3. Tool Intermediation Layer (MCP Server)"]
        MCPServer["MCP Security Server<br/>(mcp_server.py / mcp_config.json)"]
        ToolConfig["Tool Registry & Profiles<br/>(tools/tools.json)"]
        MCPServer --> ToolConfig
    end

    subgraph ExecLayer ["4. Multi-Backend Execution Environment"]
        WinHost["Windows Host (Local CLI / PowerShell)"]
        WSLKali["WSL Kali Linux Distribution"]
        DockerKali["Docker Kali Container"]
        SSHKali["Remote Kali Linux (SSH)"]
        
        MCPServer -.-> WinHost
        MCPServer -.-> WSLKali
        MCPServer -.-> DockerKali
        MCPServer -.-> SSHKali
    end

    IDE <-->|"HTTP / Streaming API"| Proxy
    Proxy <-->|"Enriched Context API"| LLMServer
    IDE <-->|"JSON-RPC (Model Context Protocol)"| MCPServer
```

### Chi tiết các tầng thành phần

| Tầng | Thành phần chính | Vai trò & Chức năng |
| :--- | :--- | :--- |
| **1. Agent Workspace** | `.agents/rules/`, `AGENTS.md`, `.agents/skills/` | Định hình vai trò chuyên gia phân tích an toàn thông tin; cung cấp hơn 70 tài liệu hướng dẫn kỹ thuật chuẩn (`SKILL.md`) để Agent tự kích hoạt theo ngữ cảnh nhiệm vụ. |
| **2. Traffic & Proxy** | `proxy_relay.py`, `bridge.md`, `memory.json` | Đóng vai trò Reverse Proxy trung gian: nạp thêm chỉ dẫn kỹ thuật (`bridge.md`), ghi nhận tiến trình phân tích vào bộ nhớ phiên (`memory.json`), và hiển thị giao diện giám sát trực quan tại cổng `8090`. |
| **3. MCP Tool Server** | `mcp_server.py`, `.agents/mcp_config.json`, `tools/tools.json` | Cung cấp giao diện chuẩn Model Context Protocol (MCP) dạng stdio hoặc HTTP, cho phép Agent khám phá và gọi hơn 30 công cụ an ninh một cách an toàn. |
| **4. Multi-Backend Engine** | Local Windows, WSL, Docker, SSH | Tự động ánh xạ và chuyển tiếp các câu lệnh công cụ tới môi trường phù hợp (ví dụ: chạy Ghidra trên Windows, chạy Nmap/SQLmap qua WSL Kali Linux). |

---

## 🔄 Luồng Hoạt động (Operational Workflow)

Dưới đây là chu trình tương tác hoàn chỉnh từ khi người dùng nhập yêu cầu đến lúc thu được kết quả kiểm thử an toàn:

```mermaid
sequenceDiagram
    autonumber
    actor User as Chuyên viên / Người dùng
    participant IDE as Antigravity IDE
    participant Proxy as Proxy Relay (:8091)
    participant LLM as Upstream LLM Server
    participant MCP as MCP Security Server
    participant Backend as Môi trường (WSL/Kali/Host)

    User->>IDE: Gửi yêu cầu phân tích / kiểm thử
    activate IDE
    Note over IDE: Nạp Rules & tự động chọn Skill phù hợp
    IDE->>Proxy: Gửi API Request kèm prompt & ngữ cảnh
    activate Proxy
    
    Proxy->>Proxy: Nạp Context bổ sung từ bridge.md & memory.json
    Proxy->>LLM: Gửi Prompt hoàn chỉnh tới LLM
    activate LLM
    
    LLM-->>Proxy: Trả về kế hoạch & Yêu cầu gọi công cụ (Tool Call)
    deactivate LLM
    Proxy-->>IDE: Stream phản hồi & chỉ định MCP Tool Call
    deactivate Proxy
    
    IDE->>MCP: Gọi Tool thông qua giao thức MCP (JSON-RPC)
    activate MCP
    Note over MCP: Tra cứu schema trong tools.json & định tuyến backend
    
    MCP->>Backend: Thực thi lệnh (Nmap, Ghidra, Frida, SQLmap...)
    activate Backend
    Backend-->>MCP: Trả về kết quả đầu ra (stdout, stderr, exit code)
    deactivate Backend
    
    MCP-->>IDE: Phản hồi Tool Result chuẩn hóa
    deactivate MCP
    
    IDE->>Proxy: Gửi lại Tool Result để tiếp tục phân tích
    activate Proxy
    Proxy->>LLM: Gửi Tool Output để tổng hợp kết luận
    activate LLM
    LLM-->>Proxy: Trả về kết quả đánh giá / Báo cáo kỹ thuật
    deactivate LLM
    Proxy-->>IDE: Kết quả hoàn thiện
    deactivate Proxy
    
    IDE-->>User: Trình bày báo cáo, bằng chứng & kiến nghị bảo mật
    deactivate IDE
```

### Các giai đoạn thực thi cụ thể

1. **Giai đoạn 1: Tiếp nhận yêu cầu & Định hướng nghiệp vụ**
   - Người dùng mô tả mục tiêu kiểm thử (ví dụ: *"Đánh giá an toàn API endpoint /v1/auth"* hoặc *"Phân tích tệp thực thi target.exe"*).
   - Antigravity IDE đối chiếu từ khóa và nạp quy tắc từ `.agents/rules/` cùng Skill chuyên biệt tương ứng (như `api-security` hoặc `ida-reverse`).

2. **Giai đoạn 2: Điều phối qua Proxy Relay**
   - Yêu cầu được gửi qua cổng Proxy `8091`.
   - Proxy tiêm nạp cấu trúc ngữ cảnh kỹ thuật từ `bridge.md`, cập nhật bộ đếm và trạng thái phiên vào `memory.json`.
   - Lưu lượng được gửi lên mô hình ngôn ngữ ở thượng nguồn (Upstream LLM).

3. **Giai đoạn 3: Phân tích & Lập kế hoạch gọi công cụ (Inference & Tool Calling)**
   - Mô hình phân tích bài toán, xác định các bước kiểm thử và phát sinh lệnh gọi công cụ MCP (ví dụ: `nmap_scan`, `strings_extract`, `sqlmap_scan`).

4. **Giai đoạn 4: Điều hướng & Thực thi công cụ đa nền tảng**
   - `mcp_server.py` tiếp nhận yêu cầu gọi công cụ, kiểm tra tham số đầu vào theo danh mục `tools/tools.json`.
   - Dựa trên cấu hình (`--backend wsl` hoặc `docker`), server tự động đóng gói lệnh và chuyển đến WSL Kali hoặc Docker container để thực thi an toàn.

5. **Giai đoạn 5: Tổng hợp bằng chứng & Báo cáo**
   - Đầu ra của công cụ được nạp ngược lại vào chuỗi hội thoại của LLM.
   - Agent phân tích dữ liệu, suy luận nguyên nhân gốc rễ và tổng hợp thành báo cáo kỹ thuật rõ ràng với đầy đủ bằng chứng (PoC) và giải pháp khắc phục.

---

## 🗂️ Cấu trúc Thư mục Dự án

```
d:\Antigravity-project\
├── .agents/
│   ├── rules/
│   │   └── nerv-bridge.md      # Quy chuẩn context engineering cho Antigravity
│   ├── skills/                 # Thư viện 70+ kỹ năng bảo mật chuẩn SKILL.md
│   │   ├── api-security/       # Kiểm thử bảo mật REST/GraphQL/WebSocket API
│   │   ├── apk-reverse/        # Phân tích & dịch ngược ứng dụng Android
│   │   ├── code-audit/         # Đánh giá an ninh mã nguồn & quy chuẩn SAST
│   │   ├── ida-reverse/        # Phân tích nhị phân với IDA Pro
│   │   ├── pwn-chain/          # Kỹ thuật khai thác lỗ hổng bộ nhớ
│   │   └── ...                 # Các modules kỹ năng chuyên sâu khác
│   └── mcp_config.json         # File đăng ký MCP Server cho Antigravity
├── AGENTS.md                   # Chỉ thị hệ thống toàn cục cho Agent
├── mcp_server.py               # MCP Server cung cấp 30+ công cụ bảo mật
├── proxy_relay.py              # Proxy điều phối lưu lượng & Web Dashboard
├── antigravity_deploy.py       # Công cụ tự động triển khai (Workspace / Global)
├── verify_antigravity.py       # Công cụ kiểm tra toàn vẹn & chẩn đoán hệ thống
├── tools/
│   └── tools.json              # Danh mục công cụ, tham số và template lệnh
├── scripts/
│   └── lab_antigravity.bat     # Menu khởi chạy nhanh bảng điều khiển
├── bridge.md                   # Mẫu ngữ cảnh kỹ thuật chuyên sâu
└── memory.json                 # Kernel lưu trữ trạng thái phiên làm việc
```

---

## 🚀 Hướng dẫn Cài đặt & Triển khai

### 1. Triển khai vào Workspace hiện tại (`.agents`)

Áp dụng toàn bộ cấu hình, rules và skills vào workspace dự án hiện hành:

```powershell
python antigravity_deploy.py apply
```

### 2. Triển khai Toàn cục (Global)

Áp dụng cấu hình dùng chung cho tất cả các Workspace trong Antigravity IDE (`~/.gemini/config`):

```powershell
python antigravity_deploy.py apply --global
```

### 3. Kiểm tra Tính toàn vẹn & Chẩn đoán

Chạy script chẩn đoán để xác nhận các thành phần Rules, Skills, MCP Server và cấu hình đã sẵn sàng:

```powershell
python verify_antigravity.py
```

### 4. Khởi chạy Hệ thống Điều phối & Giám sát

Sử dụng script điều khiển tích hợp:

```bat
scripts\lab_antigravity.bat
```

Hoặc khởi chạy từng thành phần thủ công:

- **Khởi động Proxy Relay & Web Dashboard:**
  ```powershell
  python proxy_relay.py --listen 127.0.0.1:8091 --web-port 8090
  ```
  *Truy cập Web Dashboard tại:* `http://127.0.0.1:8090`

- **Kiểm thử MCP Server ở chế độ độc lập:**
  ```powershell
  python mcp_server.py --port 9000
  ```

---

## ⚙️ Cấu hình Tùy biến Backend MCP

Trong file `.agents/mcp_config.json`, bạn có thể chỉ định backend thực thi phù hợp với môi trường của mình:

```json
{
  "mcpServers": {
    "nerv-tools": {
      "command": "python",
      "args": [
        "-u",
        "d:/Antigravity-project/mcp_server.py",
        "--backend", "wsl",
        "--wsl-distro", "kali-linux",
        "--profile", "safe"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Các tùy chọn `--backend` hỗ trợ:**
- `local`: Thực thi trực tiếp binary có sẵn trên Windows Host.
- `wsl`: Thực thi thông qua WSL (mặc định phân phối `kali-linux`).
- `docker`: Thực thi trong Docker container chứa sẵn công cụ (ví dụ: `kali-tools`).
- `ssh`: Kết nối và thực thi qua SSH tới máy chủ Kali chuyên dụng từ xa (`--ssh user@host`).
