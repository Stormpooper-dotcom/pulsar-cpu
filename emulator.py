class PulsarCPU:
    def __init__(self):
        self.ram = [0x0000]*4096
        self.acc = 0x0000 # Accumulator: lda goes here, operations go here
        self.imm = 0x0000 # Immediator: ldi goes here, transient
        self.imm_flag = False # False = don't use imm for operation
        self.pc = 0x000
        self.sp = 0xFFF # Stack is from 0xFFF to 0xF00 inclusive
        self.running = False

        self.opcodes = {
            0x0: self._hrt,
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
            0xB: self._io,
            0xC: self._cll,
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


    def _hrt(self, arg):
        if self.sp == 0xFFF or arg == 0: # Returning from the root sequence ie main() ends the program.
            self.running = False
        else:
            self.sp += 1
            self.pc = self.ram[self.sp]
            self.ram[self.sp] = 0

    def _ldi(self, arg):
        self.imm = arg
        self.imm_flag = True

    def _lda(self, arg):
        self.acc = self.ram[arg]

    def _sta(self, arg):
        if self.imm_flag:
            self.ram[arg] = self.imm
            self.imm_flag = False
        else:
            self.ram[arg] = self.acc

    def _add(self, arg):
        if self.imm_flag:
            operand = self.imm
            self.imm_flag = False
        else:
            operand = self.ram[arg]
        result = self.acc + operand
        self.acc = result & 0xFFFF

    def _sub(self, arg):
        if self.imm_flag:
            operand = self.imm
            self.imm_flag = False
        else:
            operand = self.ram[arg]
        result = self.acc - operand
        self.acc = result & 0xFFFF

    def _mul(self, arg):
        op1 = self.to_signed(self.acc)
        if self.imm_flag:
            op2 = self.to_signed(self.imm)
            self.imm_flag = False
        else:
            op2 = self.to_signed(self.ram[arg])
        result = op1 * op2
        self.acc = result & 0xFFFF

    def _div(self, arg):
        if self.imm_flag:
            operand = self.imm
            self.imm_flag = False
        else:
            operand = self.ram[arg]
            if operand != 0:
                result = int(self.acc / operand)
            else: self.running = False; return
        self.acc = result & 0xFFFF

    def _or(self, arg):
        if self.imm_flag:
            self.acc = self.acc | self.imm
            self.imm_flag = False
        else:
            self.acc = self.acc | self.ram[arg]

    def _and(self, arg):
        if self.imm_flag:
            self.acc = self.acc & self.imm
            self.imm_flag = False
        else:
            self.acc = self.acc & self.ram[arg]

    def _xor(self, arg):
        if self.imm_flag:
            self.acc = self.acc ^ self.imm
            self.imm_flag = False
        else:
            self.acc = self.acc ^ self.ram[arg]

    def _io(self, arg):
        match arg:
            case 0:
                print(self.acc, end="")
            case 1:
                print(chr(self.acc), end="")
            case 2:
                result = int(input("N? "))
                result = result & 0xFFFF
                self.acc = result
            case 3:
                result = input("C? ")
                if not result: result = "\n"
                result = ord(result[0])
                self.acc = result

    def _cll(self, arg):
        self.ram[self.sp] = self.pc
        self.sp -= 1
        if self.sp < 0xEFF:
            print("Stack overflow reached!")
            self.running = False
            return
        self.pc = arg

    def _jnz(self, arg): 
        if self.acc != 0: self.pc = arg

    def _jiz(self, arg):
        if self.acc == 0: self.pc = arg

    def _jmp(self, arg):
        self.pc = arg

# Test program
cpu = PulsarCPU()
cpu.load_binary(input("Enter binary filepath > "))
cpu.run()
print("\nCPU Halted")