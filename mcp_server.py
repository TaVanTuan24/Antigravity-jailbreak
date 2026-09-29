# -*- coding: utf-8 -*-
"""NERV-BREAK-5.6 MCP Server — Kali Linux + Security Tools

Exposes security tools as MCP tools for Codex CLI.
Supports: nmap, sqlmap, hydra, metasploit, john, hashcat, wireshark, burp, etc.

Usage:
  python mcp_server.py                          # stdio mode (Codex MCP)
  python mcp_server.py --port 9000              # HTTP mode (debug)
  python mcp_server.py --kali --ssh root@kali   # Remote Kali via SSH

Author: zxwn
"""
import sys, os, json, subprocess, threading, time, re, shlex
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE = Path(__file__).resolve().parent

# ═══════════════════════════════════════════════════════════
# TOOL DEFINITIONS — loaded from tools/tools.json
# ═══════════════════════════════════════════════════════════
def load_tools():
    """Load tool definitions from tools/tools.json, fallback to built-in."""
    tools_file = BASE / "tools" / "tools.json"
    if tools_file.exists():
        try:
            data = json.loads(tools_file.read_text(encoding="utf-8"))
            tools = {}
            config = data.get("_config", {})
            for t in data.get("tools", []):
                tools[t["name"]] = {
                    "description": t["desc"],
                    "params": t["params"],
                    "cmd": t["cmd"],
                }
            return tools, config
        except Exception as e:
            print(f"[MCP] Warning: tools.json error: {e}, using defaults", file=sys.stderr)
    return _BUILTIN_TOOLS, {}

_BUILTIN_TOOLS = {
    "python_exec": {"description": "Execute Python code", "params": ["code"], "cmd": "python -c '{code}'"},
    "shell_exec": {"description": "Execute shell command", "params": ["command"], "cmd": "{command}"},
    "powershell_exec": {"description": "Execute PowerShell command", "params": ["command"], "cmd": "powershell -Command \"{command}\""},
}
TOOLS = {}
TOOL_CONFIG = {}

# ═══════════════════════════════════════════════════════════
# BACKENDS — Kali Linux access methods
# ═══════════════════════════════════════════════════════════
BACKEND = "local"       # local | wsl | docker | ssh
KALI_SSH = None         # "root@192.168.1.100"
DOCKER_CONTAINER = None # "kali-tools"
WSL_DISTRO = "kali-linux"

def detect_backend():
    """Auto-detect available Kali backend."""
    global BACKEND
    # Check WSL
    try:
        r = subprocess.run(["wsl", "-d", WSL_DISTRO, "echo", "OK"], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30)
        if "OK" in r.stdout:
            BACKEND = "wsl"
            return "wsl"
    except: pass
    # Check Docker
    try:
        r = subprocess.run(["docker", "ps", "--filter", "name=kali-tools", "--format", "{{.Names}}"], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)
        if "kali" in r.stdout.lower():
            DOCKER_CONTAINER = r.stdout.strip()
            BACKEND = "docker"
            return "docker"
    except: pass
    return "local"

def to_wsl_path(cmd_str: str) -> str:
    r"""Convert Windows file paths like D:\dir\file to /mnt/d/dir/file."""
    return re.sub(
        r'([a-zA-Z]):[\\/]([^\s"\'<>]*)',
        lambda m: f"/mnt/{m.group(1).lower()}/{m.group(2).replace(chr(92), '/')}",
        cmd_str
    )

def run_tool(cmd, tool_name=None, category=None, timeout=600):
    """Execute tool via current backend with proper path translation and stdin isolation."""
    # Windows-specific tools must run locally on Windows
    if category == "windows" or tool_name in ["powershell_exec", "reg_query", "wmic_query"]:
        try:
            r = subprocess.run(
                cmd, shell=True, stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=timeout, cwd=str(BASE)
            )
            return r.stdout + ("\n" + r.stderr if r.stderr else "")
        except Exception as e:
            return f"Error executing Windows tool: {e}"

    if BACKEND == "wsl":
        wsl_cmd = to_wsl_path(cmd)
        r = subprocess.run(
            ["wsl", "-d", WSL_DISTRO, "bash", "-c", wsl_cmd],
            stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout + ("\n" + r.stderr if r.stderr else "")
    elif BACKEND == "docker":
        r = subprocess.run(
            ["docker", "exec", DOCKER_CONTAINER or "kali-tools", "bash", "-c", cmd],
            stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout + ("\n" + r.stderr if r.stderr else "")
    elif BACKEND == "ssh":
        r = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5", KALI_SSH, cmd],
            stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout + ("\n" + r.stderr if r.stderr else "")
    else:
        # Local Windows — try directly, fall back to wsl if command not found
        try:
            r = subprocess.run(cmd, shell=True, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout, cwd=str(BASE))
            return r.stdout + ("\n" + r.stderr if r.stderr else "")
        except Exception as e:
            # Fallback to WSL
            try:
                wsl_cmd = to_wsl_path(cmd)
                r = subprocess.run(["wsl", "-d", WSL_DISTRO, "bash", "-c", wsl_cmd], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
                return r.stdout + ("\n" + r.stderr if r.stderr else "")
            except:
                return f"Error: {e}\nCommand: {cmd}"

# ═══════════════════════════════════════════════════════════
# MCP Protocol Handler
# ═══════════════════════════════════════════════════════════
def handle_request(req: dict) -> dict:
    """Process MCP JSON-RPC request."""
    method = req.get("method", "")
    req_id = req.get("id")
    
    # Notifications in JSON-RPC (requests without id) MUST NOT receive a response
    if req_id is None:
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "nerv-break", "version": "5.6"},
                "capabilities": {
                    "tools": {"listChanged": False}
                },
            }
        }
    
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    elif method == "tools/list":
        tools_list = []
        for name, info in TOOLS.items():
            tools_list.append({
                "name": name,
                "description": info.get("description", ""),
                "inputSchema": {
                    "type": "object",
                    "properties": {p: {"type": "string"} for p in info.get("params", [])},
                    "required": info.get("params", []),
                }
            })
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools_list}}
    
    elif method == "resources/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"resources": []}}

    elif method == "prompts/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"prompts": []}}

    elif method == "tools/call":
        p = req.get("params", {})
        tool_name = p.get("name", "")
        args = p.get("arguments", {})
        
        if tool_name not in TOOLS:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}
        
        info = TOOLS[tool_name]
        try:
            # Build command with sensible fallback defaults
            clean_args = {}
            for key in info.get("params", []):
                val = args.get(key)
                if val is None or val == "":
                    if key == "min_len": val = "4"
                    elif key == "ports": val = "1-1000"
                    elif key == "port": val = "80"
                    elif key == "count": val = "10"
                    elif key == "flags": val = ""
                    elif key == "commands": val = "i"
                    elif key == "output_dir": val = "output"
                    elif key == "wordlist": val = "/usr/share/wordlists/dirb/common.txt"
                    else: val = ""
                clean_args[key] = str(val).replace("'", "'\"'\"'")
            
            cmd = info["cmd"].format(**clean_args)
            
            # Execute via appropriate backend
            output = run_tool(cmd, tool_name=tool_name, category=info.get("category"))
            output = output[:100000]  # Truncate huge output
            
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": output or "(no output)"}]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Error: {e}"}],
                    "isError": True,
                }
            }
    
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def stdio_loop():
    """MCP stdio transport — read JSON-RPC from stdin, write to stdout."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            req = json.loads(line)
            resp = handle_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            continue
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[MCP] Exception in stdio loop: {e}", file=sys.stderr)

def http_loop(port):
    """MCP HTTP transport — for debugging."""
    import http.server
    
    class MCPHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            req = json.loads(body)
            resp = handle_request(req)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            if resp:
                self.wfile.write(json.dumps(resp).encode())
        def do_GET(self):
            self.send_response(200); self.end_headers()
            self.wfile.write(b"MCP server running")
        def log_message(self, *args): pass
    
    print(f"[MCP] HTTP server on port {port}", file=sys.stderr)
    http.server.ThreadingHTTPServer(("127.0.0.1", port), MCPHandler).serve_forever()

if __name__ == "__main__":
    # Load tools from tools.json
    loaded_tools, loaded_config = load_tools()
    TOOLS.clear(); TOOLS.update(loaded_tools)
    TOOL_CONFIG.clear(); TOOL_CONFIG.update(loaded_config)
    
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, help="HTTP port for debug mode")
    ap.add_argument("--kali", metavar="SSH", help="Kali SSH address (user@host)")
    ap.add_argument("--wsl", action="store_true", help="Use WSL Kali Linux")
    ap.add_argument("--docker", metavar="CONTAINER", help="Use Docker container")
    ap.add_argument("--auto", action="store_true", help="Auto-detect best backend")
    ap.add_argument("--backend", choices=["local", "wsl", "docker", "ssh"], help="Backend type")
    ap.add_argument("--wsl-distro", default="kali-linux", help="WSL distribution name")
    ap.add_argument("--profile", help="Profile name")
    args = ap.parse_args()
    
    if args.wsl_distro:
        WSL_DISTRO = args.wsl_distro
        
    if args.backend:
        BACKEND = args.backend
        print(f"[MCP] Backend set to: {BACKEND}", file=sys.stderr)
    elif args.auto:
        backend = detect_backend()
        print(f"[MCP] Auto-detected backend: {backend}", file=sys.stderr)
    elif args.wsl:
        BACKEND = "wsl"
        print(f"[MCP] WSL Kali: {WSL_DISTRO}", file=sys.stderr)
    elif args.docker:
        BACKEND = "docker"
        DOCKER_CONTAINER = args.docker
        print(f"[MCP] Docker: {args.docker}", file=sys.stderr)
    elif args.kali:
        BACKEND = "ssh"
        KALI_SSH = args.kali
        print(f"[MCP] Kali SSH: {KALI_SSH}", file=sys.stderr)
    else:
        # Try auto-detect first, fall back to local
        backend = detect_backend()
        print(f"[MCP] Backend: {backend}", file=sys.stderr)
    
    if args.port:
        http_loop(args.port)
    else:
        stdio_loop()
