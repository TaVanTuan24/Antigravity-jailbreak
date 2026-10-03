import struct, os, subprocess

unpacked_file = r'D:\Antigravity-project\Temp\shiriken_unpacked.elf'
cracked_file = r'D:\Antigravity-project\Temp\shiriken_cracked.elf'

with open(unpacked_file, 'rb') as f:
    data = bytearray(f.read())

patches = []

# Patch 1: Root check bypass at 0x2ABFAC
# Original: cbz w0, 2abff4 (0x34000240)
# New:      b 2abff4 (0x14000012)
patches.append({
    'offset': 0x2ABFAC,
    'old': data[0x2ABFAC:0x2ABFAC+4],
    'new': struct.pack('<I', 0x14000012),
    'desc': 'Bypass geteuid root check (cbz -> b 2abff4)'
})

# Patch 2: Auth check branch at 0x2AC008
# Original: tbnz w0, #0, 2ac030 (0x37000140)
# New:      b 2ac030 (0x1400000A)
patches.append({
    'offset': 0x2AC008,
    'old': data[0x2AC008:0x2AC008+4],
    'new': struct.pack('<I', 0x1400000A),
    'desc': 'Force jump to success path post-auth (tbnz -> b 2ac030)'
})

# Patch 3: Function 0x2AC7D4 (Auth routine)
# Replace start with:
#   mov w1, #1        (0x52800021)
#   strb w1, [x0]     (0x39000001)
#   mov w0, #1        (0x52800020)
#   ret               (0xD65F03C0)
func_patch = struct.pack('<4I', 0x52800021, 0x39000001, 0x52800020, 0xD65F03C0)
patches.append({
    'offset': 0x2AC7D4,
    'old': data[0x2AC7D4:0x2AC7D4+16],
    'new': func_patch,
    'desc': 'Short-circuit auth function 0x2AC7D4 -> set auth=1, return 1'
})

print(f"Applying {len(patches)} patches...")
for p in patches:
    print(f"[+] Patch at 0x{p['offset']:X}: {p['desc']}")
    print(f"    Old: {p['old'].hex()} | New: {p['new'].hex()}")
    data[p['offset']:p['offset']+len(p['new'])] = p['new']

with open(cracked_file, 'wb') as f:
    f.write(data)

print(f"[+] Cracked ELF written to {cracked_file}")

# Verify disassembly with objdump in Kali
cmd = ["wsl", "-d", "kali-linux", "bash", "-c", "aarch64-linux-gnu-objdump -d --start-address=0x2abfa0 --stop-address=0x2ac018 /mnt/d/Antigravity-project/Temp/shiriken_cracked.elf"]
r = subprocess.run(cmd, capture_output=True, text=True)
print("\n=== Verified main() check patches ===")
print(r.stdout)

cmd2 = ["wsl", "-d", "kali-linux", "bash", "-c", "aarch64-linux-gnu-objdump -d --start-address=0x2ac7d0 --stop-address=0x2ac7f0 /mnt/d/Antigravity-project/Temp/shiriken_cracked.elf"]
r2 = subprocess.run(cmd2, capture_output=True, text=True)
print("\n=== Verified 0x2AC7D4 auth function patch ===")
print(r2.stdout)
