class PulsarCPU:
    def __init__(self):
        self.ram = [0x0000]*4096
        self.acc = 0x0000
        self.pc = 0x000
        self.sp = 0xE10
        self.running = False

        self.flag_z = 0
        self.flag_n = 0
        self.flag_o = 0

        self.opcodes = {
            0x0: self._hlt,
            0x1: self._ldi,
            0x2: self._lda,
            0x3: self._sta,
            0x4: self._add,
            0x5: self._sub,
            0x6: self._mul,
            0x7: self._div,
            0x8: self._or,
            0x9: self._and,
            0xA: self._xor,
            0xB: self._in,
            0xC: self._out,
            0xD: self._jnz,
            0xE: self._jiz,
            0xF: self._jmp,
        }

    def load_binary(self, filepath):
        try:
            with open(filepath, "rb") as f:
                bindata = f.read()

            words_count = len(bindata) // 2

            for i in range(words_count):
                if i >= len(self.ram):
                    print(f"File too big for ram lol :)")
                    break

                high_byte = bindata[i * 2]
                low_byte = bindata[i * 2 + 1]

                self.ram[i] = (high_byte << 8) | low_byte

            print(f"Successfully loaded {words_count} words into RAM.")
        except FileNotFoundError:
            print(f"Error: file {filepath} not found.")

    def run(self):
        self.running = True
        while self.running:
            instruction = self.ram[self.pc]

            opcode = (instruction >> 12) & 0xF
            arg = instruction & 0x0FFF

            #print(f"ACC: {hex(self.acc)} PC: {hex(self.pc)} Instruction: {hex(instruction)}")

            self.pc += 1

            if opcode in self.opcodes:
                self.opcodes[opcode](arg)
            else:
                print(f"Unknown opcode: {hex(opcode)}")
                self.running = False

            if not self.running: break

    def to_signed(self, val):
        val = val & 0xFFFF
        if val & 0x8000:
            return val - 0x10000
        return val


    def _hlt(self, arg):
        self.running = False

    def _ldi(self, arg):
        self.acc = arg

    def _lda(self, arg):
        self.acc = self.ram[arg]

    def _sta(self, arg):
        self.ram[arg] = self.acc

    def _add(self, arg):
        operand = self.ram[arg]
        result = self.acc + operand
        self.flag_o = int(((self.acc ^ result) & (operand ^ result) & 0x8000) != 0)
        self.acc = result & 0xFFFF
        self.flag_z = int(self.acc == 0)
        self.flag_n = int((self.acc & 0x8000) != 0)

    def _sub(self, arg): 
        operand = self.ram[arg]
        result = self.acc - operand
        self.flag_o = int(((self.acc ^ operand) & (self.acc ^ result) & 0x8000) != 0)
        self.acc = result & 0xFFFF
        self.flag_z = int(self.acc == 0)
        self.flag_n = int((self.acc & 0x8000) != 0)

    def _mul(self, arg):
        op1 = self.to_signed(self.acc)
        op2 = self.to_signed(self.ram[arg])
        result = op1 * op2
        self.flag_o = int(result < -32768 or result > 32767)
        self.acc = result & 0xFFFF
        self.flag_z = int(self.acc == 0)
        self.flag_n = int((self.acc & 0x8000) != 0)

    def _div(self, arg):
        operand = self.ram[arg]
        if operand != 0:
            result = int(self.acc / operand)
        else: self.running = False; return
        self.acc = result & 0xFFFF
        self.flag_z = int(self.acc == 0)
        self.flag_n = int((self.acc & 0x8000) != 0)

    def _or(self, arg):
        self.acc = self.acc | self.ram[arg]
        self.flag_z = int(self.acc == 0)
        self.flag_n = int((self.acc & 0x8000) != 0)

    def _and(self, arg):
        self.acc = self.acc & self.ram[arg]
        self.flag_z = int(self.acc == 0)
        self.flag_n = int((self.acc & 0x8000) != 0)

    def _jmp(self, arg): self.pc = arg

    def _xor(self, arg):
        self.acc = self.acc ^ self.ram[arg]
        self.flag_z = int(self.acc == 0)
        self.flag_n = int((self.acc & 0x8000) != 0)

    def _in(self, arg):
        user_input = input("? ")
        if not user_input: self.acc = 0x00A #('\n')
        else: self.acc = ord(user_input[0]) & 0xFFFF
        self.flag_z = int(self.acc == 0)
        self.flag_n = int((self.acc & 0x8000) != 0)

    def _out(self, arg):
        # Not fully implemeted yet
        char_code = self.acc & 0xFF
        print(chr(char_code), end="", flush=True)

    def _jnz(self, arg): 
        if not self.flag_z: self.pc = arg
    def _jiz(self, arg):
        if self.flag_z: self.pc = arg


# Test program
cpu = PulsarCPU()
cpu.load_binary(input("Enter binary filepath > "))
cpu.run()
print("\nCPU Halted")