import os, shutil, hashlib

src_packed = r'D:\Antigravity-project\Temp\shiriken_cracked_packed.elf'
src_unpacked = r'D:\Antigravity-project\Temp\shiriken_cracked.elf'

ctf_dir = r'D:\Antigravity-project\CTF'

dst_packed = os.path.join(ctf_dir, 'kzteam•shiriken_cracked.sh')
dst_unpacked = os.path.join(ctf_dir, 'kzteam•shiriken_unpacked_cracked.sh')

shutil.copy2(src_packed, dst_packed)
shutil.copy2(src_unpacked, dst_unpacked)

print(f"[+] Output file 1 (Packed):   {dst_packed} ({os.path.getsize(dst_packed)} bytes)")
print(f"    SHA256: {hashlib.sha256(open(dst_packed, 'rb').read()).hexdigest()}")

print(f"[+] Output file 2 (Unpacked): {dst_unpacked} ({os.path.getsize(dst_unpacked)} bytes)")
print(f"    SHA256: {hashlib.sha256(open(dst_unpacked, 'rb').read()).hexdigest()}")
