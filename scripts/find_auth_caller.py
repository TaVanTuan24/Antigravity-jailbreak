import struct

with open(r'D:\Antigravity-project\Temp\shiriken_unpacked.elf', 'rb') as f:
    data = f.read()

text_start = 0x000f79f0
text_size = 0x00225c54
text_end = text_start + text_size

target = 0x2AC7D4

print(f"Finding calls to 0x{target:X}...")
for offset in range(text_start, text_end - 4, 4):
    insn = struct.unpack('<I', data[offset:offset+4])[0]
    if (insn & 0xFC000000) == 0x94000000:
        imm26 = insn & 0x03FFFFFF
        if imm26 & (1 << 25):
            imm26 -= (1 << 26)
        dest = offset + (imm26 << 2)
        if dest == target:
            print(f"BL at 0x{offset:X} -> 0x{dest:X}")
