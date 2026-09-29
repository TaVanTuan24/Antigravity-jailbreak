import capstone

with open(r'D:\Antigravity-project\CTF\PouRia-Kernel(V1.0.6).sh', 'rb') as f:
    data = f.read()

md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)

# Disassemble 0xd1f00 to 0xd2700
chunk = data[0xd1f00:0xd2d00]
for ins in md.disasm(chunk, 0xd1f00):
    # Highlight branches, compares, calls, and string loads
    extra = ''
    if ins.mnemonic.startswith('b') or ins.mnemonic.startswith('cb') or ins.mnemonic.startswith('tb'):
        extra = f'  <--- BRANCH {ins.op_str}'
    elif ins.mnemonic.startswith('cmp') or ins.mnemonic.startswith('cset') or ins.mnemonic.startswith('csel'):
        extra = f'  <--- COND {ins.op_str}'
    elif 'f80' in ins.op_str:
        extra = '  [*** LOGIN SUCCESSFUL ***]'
    elif 'fe0' in ins.op_str:
        extra = '  [*** LOGIN FAILED ***]'
    elif 'f50' in ins.op_str:
        extra = '  [*** AUTHENTICATING ***]'
    print(f'{hex(ins.address)}: {ins.mnemonic:10s} {ins.op_str}{extra}')
