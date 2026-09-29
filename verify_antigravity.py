# -*- coding: utf-8 -*-
"""Verification & Diagnostic Suite for NERV-BREAK-Antigravity.

Checks rules, skills, MCP configuration, proxy, and environment setup.

Author: Antigravity Deepmind Team
"""

import os
import sys
import json
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent

def check_rule_file():
    rule_path = BASE_DIR / ".agents" / "rules" / "nerv-bridge.md"
    if not rule_path.exists():
        return False, f"Rule file missing at {rule_path}"
    content = rule_path.read_text(encoding="utf-8")
    if "NERV-BREAK-Antigravity Context Engineering Protocol" not in content:
        return False, "Rule file header missing"
    return True, f"Rule file valid ({len(content)} bytes)"

def check_agents_md():
    agents_path = BASE_DIR / "AGENTS.MD"
    if not agents_path.exists():
        return False, f"AGENTS.MD missing at {agents_path}"
    content = agents_path.read_text(encoding="utf-8")
    if "NERV_BREAK_ANTIGRAVITY" not in content:
        return False, "AGENTS.MD missing NERV protocol header"
    return True, f"AGENTS.MD valid ({len(content)} bytes)"

def check_skills():
    skills_dir = BASE_DIR / ".agents" / "skills"
    if not skills_dir.exists():
        return False, "Skills directory missing"
    count = sum(1 for _ in skills_dir.rglob("SKILL.md"))
    if count == 0:
        return False, "No SKILL.md modules found"
    return True, f"Found {count} skill modules"

def check_mcp_config():
    mcp_path = BASE_DIR / ".agents" / "mcp_config.json"
    if not mcp_path.exists():
        return False, "mcp_config.json missing"
    try:
        data = json.loads(mcp_path.read_text(encoding="utf-8"))
        if "mcpServers" not in data or "nerv-tools" not in data["mcpServers"]:
            return False, "mcp_config.json missing nerv-tools definition"
        return True, "mcp_config.json valid JSON schema"
    except Exception as e:
        return False, f"mcp_config.json invalid JSON: {e}"

def check_tools_json():
    tools_path = BASE_DIR / "tools" / "tools.json"
    if not tools_path.exists():
        return False, "tools/tools.json missing"
    try:
        data = json.loads(tools_path.read_text(encoding="utf-8"))
        num_tools = len(data.get("tools", []))
        return True, f"tools.json contains {num_tools} security tools"
    except Exception as e:
        return False, f"tools.json parse error: {e}"

def check_mcp_server():
    server_path = BASE_DIR / "mcp_server.py"
    if not server_path.exists():
        return False, "mcp_server.py missing"
    return True, "mcp_server.py present"

def check_proxy():
    proxy_path = BASE_DIR / "proxy_relay.py"
    if not proxy_path.exists():
        return False, "proxy_relay.py missing"
    return True, "proxy_relay.py present"

def run_all_checks():
    print("=" * 60)
    print(" Running NERV-BREAK-Antigravity Verification Suite")
    print("=" * 60)

    checks = [
        ("Rule Protocol (.agents/rules/nerv-bridge.md)", check_rule_file),
        ("Agent Directive (AGENTS.MD)", check_agents_md),
        ("Skills Repository (.agents/skills/)", check_skills),
        ("MCP Config (.agents/mcp_config.json)", check_mcp_config),
        ("Security Tools Registry (tools/tools.json)", check_tools_json),
        ("MCP Server Script (mcp_server.py)", check_mcp_server),
        ("Refusal Tampering Proxy (proxy_relay.py)", check_proxy),
    ]

    all_passed = True
    for name, fn in checks:
        passed, msg = fn()
        status_str = "[PASS]" if passed else "[FAIL]"
        print(f" {status_str:7s} {name}: {msg}")
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print(" VERIFICATION SUCCESSFUL: All checks passed!")
    else:
        print(" VERIFICATION WARNING: Some checks failed.")
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
