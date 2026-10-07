opcodes = {
    "hlt": 0x0, "ldi": 0x1, "lda": 0x2, "sta": 0x3,
    "add": 0x4, "sub": 0x5, "mul": 0x6, "div": 0x7,
    "or":  0x8, "and": 0x9, "xor": 0xA, "in":  0xB,
    "out": 0xC, "jnz": 0xD, "jiz": 0xE, "jmp": 0xF
}


var_addr = 0xFFF
labels = {}


filepath = input("Enter file path (no extension) > ")


with open(f"{filepath}.txt", "r") as f:
    firstlines = f.readlines()
    firstlines = [line.strip().lower() for line in firstlines]


pass1lines = []
dat_count = 0  # Track how many DAT variables we have processed


# Pass 1: generate label dict
for line in firstlines:
    tokens = line.split() 
    if not tokens: continue
    
    if tokens[0] not in opcodes:
        if tokens[1] == "dat":
            labels[tokens[0]] = var_addr
            pass1lines.append(f"ldi {tokens[2]}")
            pass1lines.append(f"sta `{var_addr}")
            var_addr -= 1
            dat_count += 2  # Each DAT outputs exactly 2 lines
        else:
            # The label's true address is exactly how many lines have been written so far!
            labels[tokens[0]] = len(pass1lines)
            pass1lines.append(" ".join(tokens[1:]))
    else:
        pass1lines.append(" ".join(tokens))




pass1lines = "\n".join(pass1lines).split("\n")


pass2lines = []
# Pass 2: replace labels with addrs
for line in pass1lines:
    tokens = line.split(" ")
    if tokens[-1] not in opcodes and tokens[-1][0] not in "`1234567890":
        if tokens[-1] in labels:
            tokens[-1] = str(hex(labels[tokens[-1]]))[2:]
        else:
            raise NameError(f"Label {tokens[-1]} doesn't exist")
    pass2lines.append(" ".join(tokens))


pass3lines = []
# Pass 3: convert numbers
for line in pass2lines:
    tokens = line.split(" ")
    if len(tokens) == 1:
        tokens.append("0")
    elif tokens[-1].startswith("`"):
        tokens[-1] = str(hex(int(tokens[-1][1:])))[2:]
    pass3lines.append(" ".join(tokens))


print("\n".join(pass3lines))


with open(f"{filepath}.bin", "wb") as new_f:
    for line in pass3lines:
        line = line.strip()
        if not line: continue


        instruction = opcodes[line[:3].lower()]
        addr = int(line[4:], 16)


        new_line = (instruction << 12) + addr
        new_f.write(new_line.to_bytes(2, byteorder="big"))
