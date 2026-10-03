with open(r'D:\Antigravity-project\Temp\disasm_2ac.txt', 'r') as f:
    lines = f.readlines()

print("Occurrences of #-168 or #-0xa8 or offset 0xa8 in disasm_2ac.txt:")
for i, line in enumerate(lines):
    if "0xa8" in line or "168" in line:
        for j in range(max(0, i-2), min(len(lines), i+3)):
            print(f"{j+1}: {lines[j].strip()}")
        print("-" * 40)
