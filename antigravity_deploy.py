# -*- coding: utf-8 -*-
"""NERV-BREAK-Antigravity Deployment Tool for Antigravity Desktop

Deploys NERV-BREAK rules, skills, MCP configuration, and AGENTS directives 
globally (%USERPROFILE%\\.gemini\\config) or locally (.agents/ in workspace).

Usage:
  python antigravity_deploy.py apply              # Apply to current workspace (.agents)
  python antigravity_deploy.py apply --global     # Apply globally (~/.gemini/config)
  python antigravity_deploy.py remove             # Remove from workspace
  python antigravity_deploy.py status             # Show deployment state

Author: Antigravity Deepmind Team / NERV-BREAK Fork
"""

import os
import sys
import shutil
import json
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent
RULES_SRC = BASE_DIR / ".agents" / "rules" / "nerv-bridge.md"
SKILLS_SRC = BASE_DIR / ".agents" / "skills"
AGENTS_SRC = BASE_DIR / "AGENTS.MD"
MCP_SRC = BASE_DIR / ".agents" / "mcp_config.json"

GLOBAL_CONFIG_DIR = Path(os.path.expanduser("~/.gemini/config"))
WORKSPACE_AGENTS_DIR = BASE_DIR / ".agents"


def apply(is_global=False):
    """Deploy NERV-BREAK components to Antigravity."""
    print("=" * 60)
    print(f" Deploying NERV-BREAK-Antigravity ({'GLOBAL' if is_global else 'WORKSPACE'})")
    print("=" * 60)

    target_rules_dir = (GLOBAL_CONFIG_DIR / "rules") if is_global else (WORKSPACE_AGENTS_DIR / "rules")
    target_skills_dir = (GLOBAL_CONFIG_DIR / "skills") if is_global else (WORKSPACE_AGENTS_DIR / "skills")

    target_rules_dir.mkdir(parents=True, exist_ok=True)
    target_skills_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy Rules
    if RULES_SRC.exists():
        dst_rule = target_rules_dir / "nerv-bridge.md"
        if RULES_SRC.resolve() != dst_rule.resolve():
            shutil.copy2(RULES_SRC, dst_rule)
            print(f" [OK] Rule deployed: {dst_rule}")
        else:
            print(f" [OK] Rule present at workspace: {dst_rule}")
    else:
        print(f" [FAIL] Rule source not found at {RULES_SRC}")

    # 2. Copy Skills
    if SKILLS_SRC.exists():
        count = 0
        if SKILLS_SRC.resolve() != target_skills_dir.resolve():
            for item in SKILLS_SRC.iterdir():
                if item.is_dir():
                    dst_item = target_skills_dir / item.name
                    if dst_item.exists():
                        shutil.rmtree(dst_item)
                    shutil.copytree(item, dst_item)
                    count += 1
            print(f" [OK] {count} Skill modules deployed to {target_skills_dir}")
        else:
            count = sum(1 for item in SKILLS_SRC.iterdir() if item.is_dir())
            print(f" [OK] {count} Skill modules present at workspace: {target_skills_dir}")

    # 3. Workspace specific (AGENTS.MD & mcp_config.json)
    if not is_global:
        if AGENTS_SRC.exists():
            dst_agents = BASE_DIR / "AGENTS.MD"
            if dst_agents != AGENTS_SRC:
                shutil.copy2(AGENTS_SRC, dst_agents)
            print(f" [OK] AGENTS.MD updated at workspace root")

        if MCP_SRC.exists():
            print(f" [OK] mcp_config.json configured at {MCP_SRC}")

    print("\n [SUCCESS] Deployment complete for Antigravity Desktop!")
    return True


def remove(is_global=False):
    """Remove NERV-BREAK components."""
    print("=" * 60)
    print(f" Removing NERV-BREAK-Antigravity ({'GLOBAL' if is_global else 'WORKSPACE'})")
    print("=" * 60)

    target_rules_dir = (GLOBAL_CONFIG_DIR / "rules") if is_global else (WORKSPACE_AGENTS_DIR / "rules")
    target_skills_dir = (GLOBAL_CONFIG_DIR / "skills") if is_global else (WORKSPACE_AGENTS_DIR / "skills")

    rule_file = target_rules_dir / "nerv-bridge.md"
    if rule_file.exists():
        rule_file.unlink()
        print(f" [OK] Removed rule: {rule_file}")

    print(" [OK] Removal complete.")
    return True


def status():
    """Check current status."""
    print("=" * 60)
    print(" NERV-BREAK-Antigravity Deployment Status")
    print("=" * 60)

    # Workspace status
    ws_rule = WORKSPACE_AGENTS_DIR / "rules" / "nerv-bridge.md"
    ws_skills = WORKSPACE_AGENTS_DIR / "skills"
    ws_mcp = WORKSPACE_AGENTS_DIR / "mcp_config.json"

    print(f" Workspace Rule (.agents/rules/nerv-bridge.md): {'INSTALLED' if ws_rule.exists() else 'NOT FOUND'}")
    if ws_skills.exists():
        count = sum(1 for _ in ws_skills.rglob("SKILL.md"))
        print(f" Workspace Skills (.agents/skills/): {count} modules")
    else:
        print(" Workspace Skills: NONE")
    print(f" Workspace MCP Config (.agents/mcp_config.json): {'INSTALLED' if ws_mcp.exists() else 'NOT FOUND'}")

    # Global status
    gl_rule = GLOBAL_CONFIG_DIR / "rules" / "nerv-bridge.md"
    gl_skills = GLOBAL_CONFIG_DIR / "skills"
    print(f" Global Rule (~/.gemini/config/rules/nerv-bridge.md): {'INSTALLED' if gl_rule.exists() else 'NOT FOUND'}")
    if gl_skills.exists():
        count = sum(1 for _ in gl_skills.rglob("SKILL.md"))
        print(f" Global Skills (~/.gemini/config/skills/): {count} modules")
    else:
        print(" Global Skills: NONE")


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "status"
    is_global = "--global" in args

    if cmd == "apply":
        apply(is_global=is_global)
    elif cmd == "remove":
        remove(is_global=is_global)
    elif cmd == "status":
        status()
    else:
        print("Usage: python antigravity_deploy.py [apply|remove|status] [--global]")
