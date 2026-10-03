import subprocess

def run_bash(bash_cmd):
    cmd = ["wsl", "-d", "kali-linux", "bash", "-c", bash_cmd]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout, res.stderr

out, err = run_bash('readelf -s /mnt/d/Antigravity-project/Temp/shiriken_unpacked.elf | grep -iE "(kzteam|license|auth|login|check|verify|main|Init)" | head -n 60')
print("SYMBOLS:")
print(out)
if not out.strip():
    print("No matching symbol table found. Checking dynamic symbols (readelf -W --dyn-syms)...")
    out2, _ = run_bash('readelf -W --dyn-syms /mnt/d/Antigravity-project/Temp/shiriken_unpacked.elf | grep -iE "(kzteam|license|auth|login|check|verify|main|Init)" | head -n 60')
    print(out2)
