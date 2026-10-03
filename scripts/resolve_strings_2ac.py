import re

with open(r'D:\Antigravity-project\Temp\shiriken_unpacked.elf', 'rb') as f:
    elf_data = f.read()

# Let's inspect the disasm around 0x2abf00 to 0x2ad100
with open(r'D:\Antigravity-project\Temp\disasm_2ac.txt', 'r') as f:
    lines = f.readlines()

# Find all ADRP + ADD in this section and resolve the strings they point to
import struct
def decode_adrp(insn, pc):
    if (insn & 0x9F000000) == 0x90000000:
        rd = insn & 0x1F
        immlo = (insn >> 29) & 0x3
        immhi = (insn >> 5) & 0x7FFFF
        imm = (immhi << 2) | immlo
        if imm & (1 << 20):
            imm -= (1 << 21)
        base = (pc & ~0xFFF) + (imm << 12)
        return rd, base
    return None

def decode_add_imm(insn):
    if (insn & 0x7F800000) == 0x11000000:
        rd = insn & 0x1F
        rn = (insn >> 5) & 0x1F
        shift = (insn >> 22) & 1
        imm12 = (insn >> 10) & 0xFFF
        if shift:
            imm12 <<= 12
        return rd, rn, imm12
    return None

reg_pages = {}
for offset in range(0x2abf00, 0x2ad100, 4):
    insn = struct.unpack('<I', elf_data[offset:offset+4])[0]
    adrp = decode_adrp(insn, offset)
    if adrp:
        rd, page = adrp
        reg_pages[rd] = (offset, page)
        continue
    add = decode_add_imm(insn)
    if add:
        rd, rn, imm = add
        if rn in reg_pages:
            adrp_off, page = reg_pages[rn]
            if offset - adrp_off <= 16:
                target = page + imm
                if 0 <= target < len(elf_data):
                    # extract string at target
                    end = elf_data.find(b'\x00', target)
                    if end != -1 and end - target < 120:
                        s = elf_data[target:end]
                        try:
                            s_dec = s.decode('ascii')
                            if len(s_dec) >= 2:
                                print(f"0x{offset:X} -> string at 0x{target:X}: {repr(s_dec)}")
                        except:
                            pass
