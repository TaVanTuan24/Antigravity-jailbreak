with open(r'D:\Antigravity-project\Temp\shiriken_unpacked.elf', 'rb') as f:
    elf_data = f.read()

import re
sub = elf_data[0x95000:0x97000]
for m in re.finditer(rb'[\x20-\x7e]{3,}', sub):
    off = 0x95000 + m.start()
    print(f"0x{off:X}: {m.group().decode('latin1', errors='replace')}")
