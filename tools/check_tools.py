# -*- coding: utf-8 -*-
"""Check which tools from tools.json are available on this system."""
import json, subprocess, shutil, os, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE = Path(__file__).resolve().parent
with open(BASE / "tools.json", "r", encoding="utf-8") as f:
    data = json.load(f)

tools = data["tools"]
config = data.get("_config", {})
wsl_distro = config.get("wsl_distro", "kali-linux")
available = []
unavailable = []

print(f"检查 {len(tools)} 个工具...\n")

for t in tools:
    name = t["name"]
    # Extract the binary name from the command
    cmd = t["cmd"].split()[0]  # First word is the command
    # Map common names
    bin_name = cmd.split("/")[-1]  # Handle paths like python/module
    if bin_name in ("python", "python3"):
        available.append(name) if shutil.which(bin_name) else unavailable.append(name)
    elif bin_name in ("{command}",):
        # shell_exec is provided by the host shell rather than a fixed binary.
        available.append(name) if (shutil.which("powershell") or shutil.which("cmd")) else unavailable.append(name)
    elif bin_name in ("java", "javaw"):
        available.append(name)  # Assume Java available
    else:
        # Check if command exists
        if shutil.which(bin_name) or shutil.which(bin_name + ".exe"):
            available.append(name)
        else:
            # Check WSL
            try:
                r = subprocess.run(
                    ["wsl", "-d", wsl_distro, "which", bin_name],
                    capture_output=True, text=True, timeout=5,
                )
                if r.returncode == 0 and r.stdout.strip():
                    available.append(name)
                    continue
            except:
                pass
            unavailable.append(name)

print(f"可用: {len(available)}/{len(tools)}")
print(f"缺失: {len(unavailable)}/{len(tools)}")

if unavailable:
    print(f"\n缺失工具 ({len(unavailable)}):")
    cats = {}
    for name in unavailable:
        for t in tools:
            if t["name"] == name:
                cat = t.get("category", "other")
                cats.setdefault(cat, []).append(name)
    for cat, names in sorted(cats.items()):
        print(f"\n  [{cat}]")
        for n in names[:10]:
            print(f"    - {n}")
        if len(names) > 10:
            print(f"    ... and {len(names)-10} more")

print(f"\n安装缺失工具: tools/install.bat")
print(f"或一键装 Kali WSL: wsl --install -d kali-linux")
