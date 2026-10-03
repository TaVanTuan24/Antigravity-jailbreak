import struct

with open(r'D:\Antigravity-project\Temp\shiriken_unpacked.elf', 'rb') as f:
    elf = f.read()

# Find all calls to pthread_create
# In PLT, where is pthread_create?
import subprocess
cmd = ["wsl", "-d", "kali-linux", "bash", "-c", "readelf -r /mnt/d/Antigravity-project/Temp/shiriken_unpacked.elf | grep pthread_create"]
r = subprocess.run(cmd, capture_output=True, text=True)
print("pthread_create relocations:", r.stdout)

# Find all calls to pthread_create in .text
cmd2 = ["wsl", "-d", "kali-linux", "bash", "-c", "aarch64-linux-gnu-objdump -d /mnt/d/Antigravity-project/Temp/shiriken_unpacked.elf | grep '<pthread_create@plt>'"]
r2 = subprocess.run(cmd2, capture_output=True, text=True)
print("pthread_create calls in binary:\n", r2.stdout)
