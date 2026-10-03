"""
UltraEdit v33.0.0.23 — ProtectionPlusDLL.dll License Bypass Patcher
====================================================================
Target: ProtectionPlusDLL.dll (x64)
Method: Patch IsActivatedSoftwareKey to always return TRUE (1)

Original IsActivatedSoftwareKey at RVA 0x81c30:
  180081c30: 88 4c 24 08          mov BYTE PTR [rsp+0x8], cl
  180081c34: 48 83 ec 38          sub rsp, 0x38
  180081c38: c6 44 24 20 00       mov BYTE PTR [rsp+0x20], 0x0
  ...
  180081c6b: c6 44 24 20 01       mov BYTE PTR [rsp+0x20], 0x1   ; activated = true
  180081c70: 0f b6 44 24 20       movzx eax, BYTE PTR [rsp+0x20] ; return value
  180081c75: 48 83 c4 38          add rsp, 0x38
  180081c79: c3                   ret

Patch: Replace function prologue with:
  mov al, 1    ; B0 01
  ret          ; C3
  (pad with NOP)

Also patch IsInitializedSoftwareKey at RVA 0x81c80:
  180081c80: 48 83 ec 28          sub rsp, 0x28
  ...
  180081c9c: 32 c0                xor al, al   ; return false
  180081c9e: 48 83 c4 28          add rsp, 0x28
  180081ca2: c3                   ret

Patch: Replace with:
  mov al, 1    ; B0 01
  ret          ; C3

Also patch GetRemainingDemoDaysSoftwareKey at RVA 0x81cf0 to return 9999:
  Patch: mov eax, 9999 ; ret
"""

import struct
import shutil
import os
import sys

DLL_PATH = "/mnt/d/Apps/UltraEdit/ProtectionPlusDLL.dll"
BACKUP_PATH = DLL_PATH + ".bak"

# Parse PE sections to compute RVA -> file offset mapping

def parse_sections(data):
    pe_off = struct.unpack_from("<I", data, 0x3c)[0]
    num_sec = struct.unpack_from("<H", data, pe_off + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe_off + 20)[0]
    sec_table = pe_off + 24 + opt_size
    sections = []
    for i in range(num_sec):
        off = sec_table + i * 40
        name = data[off:off+8].rstrip(b'\x00').decode('latin-1')
        vsize, vaddr, rsize, raddr = struct.unpack_from("<IIII", data, off + 8)
        sections.append((name, vaddr, vsize, raddr, rsize))
    return sections

def rva_to_file(sections, rva):
    for name, vaddr, vsize, raddr, rsize in sections:
        if vaddr <= rva < vaddr + vsize:
            return raddr + (rva - vaddr)
    return None

with open(DLL_PATH, "rb") as f:
    data = bytearray(f.read())

sections = parse_sections(data)

patches = []

# ============================================================
# Patch 1: IsActivatedSoftwareKey (RVA 0x81c30)
# Original: 88 4c 24 08 48 83 ec 38 c6 44 24 20 00 ...
# Patched:  b0 01 c3 (mov al,1; ret) + NOP padding
# ============================================================
rva_isactivated = 0x81c30
off_isactivated = rva_to_file(sections, rva_isactivated)
original_isactivated = bytes(data[off_isactivated:off_isactivated+5])
expected_isactivated = bytes.fromhex("884c240848")
assert original_isactivated == expected_isactivated, \
    f"IsActivatedSoftwareKey signature mismatch at 0x{off_isactivated:x}: {original_isactivated.hex()} != {expected_isactivated.hex()}"

patch_isactivated = b'\xb0\x01\xc3\x90\x90'  # mov al,1; ret; nop; nop
patches.append(("IsActivatedSoftwareKey", off_isactivated, original_isactivated, patch_isactivated))

# ============================================================
# Patch 2: IsInitializedSoftwareKey (RVA 0x81c80)
# Original: 48 83 ec 28 48 83 3d ...
# Patched:  b0 01 c3 90 (mov al,1; ret; nop)
# ============================================================
rva_isinit = 0x81c80
off_isinit = rva_to_file(sections, rva_isinit)
original_isinit = bytes(data[off_isinit:off_isinit+4])
expected_isinit = bytes.fromhex("4883ec28")
assert original_isinit == expected_isinit, \
    f"IsInitializedSoftwareKey signature mismatch at 0x{off_isinit:x}: {original_isinit.hex()} != {expected_isinit.hex()}"

patch_isinit = b'\xb0\x01\xc3\x90'  # mov al,1; ret; nop
patches.append(("IsInitializedSoftwareKey", off_isinit, original_isinit, patch_isinit))

# ============================================================
# Patch 3: GetRemainingDemoDaysSoftwareKey (RVA 0x81cf0)
# Original: 89 4c 24 08 57 48 81 ec 00 03 00 00
# Patched:  b8 0f 27 00 00 c3 (mov eax, 9999; ret)
# ============================================================
rva_demo = 0x81cf0
off_demo = rva_to_file(sections, rva_demo)
original_demo = bytes(data[off_demo:off_demo+6])
print(f"GetRemainingDemoDays at offset 0x{off_demo:x}: {original_demo.hex()}")

patch_demo = b'\xb8\x0f\x27\x00\x00\xc3'  # mov eax, 9999; ret
patches.append(("GetRemainingDemoDaysSoftwareKey", off_demo, original_demo[:6], patch_demo))

# ============================================================
# Apply patches
# ============================================================
print(f"\n{'='*60}")
print(f"UltraEdit ProtectionPlusDLL.dll Patcher")
print(f"{'='*60}")

# Backup
if not os.path.exists(BACKUP_PATH):
    shutil.copy2(DLL_PATH, BACKUP_PATH)
    print(f"[+] Backup created: {BACKUP_PATH}")
else:
    print(f"[*] Backup already exists: {BACKUP_PATH}")

for name, offset, original, patch in patches:
    print(f"\n[PATCH] {name}")
    print(f"  File offset: 0x{offset:08x}")
    print(f"  Original:    {original.hex()}")
    print(f"  Patched:     {patch.hex()}")
    data[offset:offset+len(patch)] = patch

with open(DLL_PATH, "wb") as f:
    f.write(data)

print(f"\n[+] All patches applied successfully!")
print(f"[+] Patched file: {DLL_PATH}")
print(f"[+] Backup file:  {BACKUP_PATH}")
