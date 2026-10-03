import os, glob, subprocess

ctf_dir = r"D:\Antigravity-project\CTF"
files = os.listdir(ctf_dir)
target = None
for f in files:
    if "shiriken" in f:
        target = os.path.join(ctf_dir, f)
        break

print(f"Target file: {target}")

# Copy to Kali /tmp/target.elf using python binary read/write or wsl cp
with open(target, 'rb') as src:
    data = src.read()

print(f"Read {len(data)} bytes from target")

# Write to a clean temp file in D:\Antigravity-project\Temp
temp_dir = r"D:\Antigravity-project\Temp"
os.makedirs(temp_dir, exist_ok=True)
clean_input = os.path.join(temp_dir, "shiriken.elf")
with open(clean_input, 'wb') as dst:
    dst.write(data)

print(f"Written to {clean_input}")

# Run UPX in Kali
cmd = ["wsl", "-d", "kali-linux", "bash", "-c", "upx -d /mnt/d/Antigravity-project/Temp/shiriken.elf -o /mnt/d/Antigravity-project/Temp/shiriken_unpacked.elf"]
r = subprocess.run(cmd, capture_output=True, text=True)
print("UPX STDOUT:\n", r.stdout)
print("UPX STDERR:\n", r.stderr)
