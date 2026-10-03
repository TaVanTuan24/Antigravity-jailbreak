import struct

with open(r'D:\Antigravity-project\Temp\shiriken_unpacked.elf', 'rb') as f:
    data = f.read()

text_start = 0x000f79f0
text_size = 0x00225c54
text_end = text_start + text_size

targets = {
    0x31cdb4: "write_xml_func1",
    0x31d008: "write_xml_func2",
    0x2a1da8: "kzteam_ref1",
    0x2a1dfc: "kzteam_ref2",
}

print("Looking for BL calls to target functions...")
for offset in range(text_start, text_end - 4, 4):
    insn = struct.unpack('<I', data[offset:offset+4])[0]
    # BL opcode: [31:26] = 100101 (0x94000000)
    if (insn & 0xFC000000) == 0x94000000:
        imm26 = insn & 0x03FFFFFF
        if imm26 & (1 << 25):
            imm26 -= (1 << 26)
        dest = offset + (imm26 << 2)
        if dest in targets:
            print(f"BL at 0x{offset:X} -> 0x{dest:X} ({targets[dest]})")
