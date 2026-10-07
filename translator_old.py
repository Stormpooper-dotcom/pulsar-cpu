opcodes = {
    "hlt": 0x0, "ldi": 0x1, "lda": 0x2, "sta": 0x3,
    "add": 0x4, "sub": 0x5, "mul": 0x6, "div": 0x7,
    "or":  0x8, "and": 0x9, "xor": 0xA, "in":  0xB,
    "out": 0xC, "jnz": 0xD, "jiz": 0xE, "jmp": 0xF
}

filepath = input("Enter file path (no extension) > ")

# 1. Open the output file once in 'wb' (write binary) mode to overwrite old runs
with open(f"{filepath}.txt", "r") as f, open(f"{filepath}.bin", "wb") as new_f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line: 
            continue  # Skip empty lines
            
        instruction = opcodes[line[:3].lower()]
        addr = int(line[4:], 16)
        
        # 2. FIXED PRECEDENCE: Added parentheses around the bit shift.
        # Python evaluates + before <<, so (12 + addr) was happening first.
        new_line = (instruction << 12) + addr
        
        # 3. FIXED DATA TYPE: Convert the integer into 2 bytes (16-bit big-endian)
        new_f.write(new_line.to_bytes(2, byteorder='big'))
