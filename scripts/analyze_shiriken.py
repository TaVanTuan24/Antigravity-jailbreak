import re

with open(r'D:\Antigravity-project\Temp\shiriken_unpacked.elf', 'rb') as f:
    data = f.read()

sub = data[0x95000:0x9C000]
for m in re.finditer(b'[\x20-\x7e]{3,}', sub):
    s = m.group().decode('latin1')
    # Filter out noisy dwarf unwind strings if wanted, or print everything interesting
    if any(k in s for k in ['/', 'key', 'license', 'xml', 'map', 'http', 'KZ', 'kz', 'Kz', 'proc', 'pref', 'team', 'shiriken', 'date', 'auth', 'pass', 'valid', 'user', 'cmdline', 'token', 'error']):
        print(f'0x{0x95000+m.start():X}: {s}')
