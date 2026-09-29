import capstone
import struct

with open(r'D:\Antigravity-project\CTF\PouRia-Kernel(V1.0.6).sh', 'rb') as f:
    data = f.read()

md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
text_start = 0xc46c0
text_size = 0x257094

targets = ['740', 'f80', 'fe0', '400', 'f20', 'fa0', 'f50', '4e0', '4f0', '510', 'ef0', 'e20', 'de0']

for pc in range(text_start, text_start + text_size, 4):
    insn = struct.unpack('<I', data[pc:pc+4])[0]
    if (insn & 0x9f000000) == 0x90000000:
        immlo = (insn >> 29) & 3
        immhi = (insn >> 5) & 0x7ffff
        imm = (immhi << 2) | immlo
        if imm & (1 << 20):
            imm -= (1 << 21)
        target_page = (pc & ~0xfff) + (imm << 12)
        if target_page == 0x343000:
            chunk = data[pc:pc+16]
            dis = list(md.disasm(chunk, pc))
            for d in dis[1:]:
                for off_hex in targets:
                    if ('#0x' + off_hex) in d.op_str:
                        print(f"{hex(pc)}: {d.mnemonic} {d.op_str}")
