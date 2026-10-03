path = r'D:\Antigravity-project\CTF\LOADER-MLBB-V5.2\apktool\smali\com\facebook\katana\act\LoginActivity.smali'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if '.method private static synthetic lambda$Login$4(Landroid/content/Context;Ljava/lang/String;Landroid/os/Handler;)V' in line:
        start_idx = i
    if start_idx is not None and i > start_idx and line.strip() == '.end method':
        end_idx = i
        break

print(f'start_idx={start_idx} (line {start_idx+1}), end_idx={end_idx} (line {end_idx+1})')

replacement = """\
.method private static synthetic lambda$Login$4(Landroid/content/Context;Ljava/lang/String;Landroid/os/Handler;)V
    .locals 2

    const-string v0, "4070908800000"

    sput-object v0, Lcom/facebook/katana/act/MainActivity;->loginInfo:Ljava/lang/String;

    invoke-static {}, Landroid/os/Message;->obtain()Landroid/os/Message;

    move-result-object v0

    const/4 v1, 0x1

    iput v1, v0, Landroid/os/Message;->what:I

    const-string v1, "SUCCESS"

    iput-object v1, v0, Landroid/os/Message;->obj:Ljava/lang/Object;

    invoke-virtual {p2, v0}, Landroid/os/Handler;->sendMessage(Landroid/os/Message;)Z

    return-void
.end method
"""

new_lines = lines[:start_idx] + [replacement] + lines[end_idx+1:]
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Successfully patched LoginActivity.smali!')
