import struct

# In AArch64:
# ADRP Xd, label
# op: [31: 1] [30:29 immlo] [28:24 10000] [23:5 immhi] [4:0 Rd]
# ADD Xd, Xn, #imm12
# op: [31: 1 (64-bit)] [30:0] [29:0] [28:22 1000100] [21:10 imm12] [9:5 Rn] [4:0 Rd]

with open(r'D:\Antigravity-project\Temp\shiriken_unpacked.elf', 'rb') as f:
    data = f.read()

text_start = 0x000f79f0
text_size = 0x00225c54
text_end = text_start + text_size

target_addrs = {
    0x96815: '<string name="license_key">',
    0x98850: '/KzPrefs.xml',
    0x9A2D8: '/shared_prefs',
    0x9AECF: '/data/user/0/',
    0x9A229: 'KZTEAM entry is missing fields.',
    0x97189: 'kzteam'
}

print("Scanning .text for ADRP + ADD / LDR references...")

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
    # ADD Xd, Xn, #imm12 (64-bit or 32-bit)
    if (insn & 0x7F800000) == 0x11000000:
        rd = insn & 0x1F
        rn = (insn >> 5) & 0x1F
        shift = (insn >> 22) & 1
        imm12 = (insn >> 10) & 0xFFF
        if shift:
            imm12 <<= 12
        return rd, rn, imm12
    return None

def decode_ldr_imm(insn):
    # LDR (literal or immediate unsigned offset)
    # LDR Xt, [Xn, #pimm]
    # size=3 (64-bit), 1111 1001 01 imm12 Rn Rt -> 0xF9400000
    if (insn & 0xFFC00000) == 0xF9400000:
        rt = insn & 0x1F
        rn = (insn >> 5) & 0x1F
        imm12 = (insn >> 10) & 0xFFF
        return rt, rn, imm12 * 8
    # LDR Wt, [Xn, #pimm] -> 0xB9400000
    if (insn & 0xFFC00000) == 0xB9400000:
        rt = insn & 0x1F
        rn = (insn >> 5) & 0x1F
        imm12 = (insn >> 10) & 0xFFF
        return rt, rn, imm12 * 4
    return None

# Simple tracker of registers
reg_pages = {}
for offset in range(text_start, text_end - 4, 4):
    insn = struct.unpack('<I', data[offset:offset+4])[0]
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
            if offset - adrp_off <= 16:  # within a few instructions
                target = page + imm
                if target in target_addrs or any(abs(target - t) < 4 for t in target_addrs):
                    desc = target_addrs.get(target, "near target")
                    print(f"[XREF ADD] at 0x{offset:X} -> target 0x{target:X} ({desc})")
        continue

    ldr = decode_ldr_imm(insn)
    if ldr:
        rt, rn, imm = ldr
        if rn in reg_pages:
            adrp_off, page = reg_pages[rn]
            if offset - adrp_off <= 16:
                target = page + imm
                if target in target_addrs:
                    desc = target_addrs.get(target, "target")
                    print(f"[XREF LDR] at 0x{offset:X} -> target 0x{target:X} ({desc})")
