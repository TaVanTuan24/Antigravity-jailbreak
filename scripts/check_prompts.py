import struct

with open(r'D:\Antigravity-project\Temp\shiriken_unpacked.elf', 'rb') as f:
    elf = f.read()

# Let's inspect the addresses printed in 0x2AC7D4
addrs = [
    0x3574d8, 0x3574f0, 0x993de, 0x9775c, 0x97190, 0x357cf8, 0x357d10, 0x357e90, 0x357ea8
]

for a in addrs:
    if 0 <= a < len(elf):
        end = elf.find(b'\x00', a)
        print(f"0x{a:X}: {repr(elf[a:end])}")
    else:
        print(f"0x{a:X}: outside binary (len={len(elf)})")
