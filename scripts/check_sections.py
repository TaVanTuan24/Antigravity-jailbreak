import subprocess

def run_bash(bash_cmd):
    cmd = ["wsl", "-d", "kali-linux", "bash", "-c", bash_cmd]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

out, _ = run_bash('readelf -S /mnt/d/Antigravity-project/Temp/shiriken_unpacked.elf')
print("SECTIONS:")
print(out)
