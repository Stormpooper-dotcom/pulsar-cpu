import os

class PulsarAssembler:
    def __init__(self):
        self.opcodes = {
            "HRT": 0x0, "LDI": 0x1, "LDA": 0x2, "STA": 0x3,
            "ADD": 0x4, "SUB": 0x5, "MUL": 0x6, "DIV": 0x7,
            "OR":  0x8, "AND": 0x9, "XOR": 0xA, "IO":  0xB,
            "CLL": 0xC, "JNZ": 0xD, "JIZ": 0xE, "JMP": 0xF
        }
        self.labels = {}

    def parse_token(self, token):
        is_imm = False
        token = token.strip()
        
        if token.startswith("!"):
            is_imm = True
            token = token[1:].strip()

        # Handle label lookup
        if token in self.labels:
            return self.labels[token], is_imm

        if token.startswith("`"):
            val = int(token[1:], 10)
        else:
            val = int(token, 16)
            
        return val, is_imm

    def assemble(self, source_code):
        lines = source_code.splitlines()
        cleaned_instructions = []
        
        # --- PASS 1: Calculate PCs and Catalog Labels Safely ---
        current_pc = 0
        for line in lines:
            line = line.split(";")[0].strip() # Strip comments safely
            if not line:
                continue

            # FIX: Extract labels even if they are inline with an instruction (e.g., my_var: DAT `10)
            if ":" in line:
                label_part, line_part = line.split(":", 1)
                self.labels[label_part.strip()] = current_pc
                line = line_part.strip()
                if not line: # If it was just a standalone label line
                    continue

            parts = line.split(maxsplit=1)
            mnemonic = parts[0].upper()
            arg_str = parts[1].strip() if len(parts) > 1 else ""

            if mnemonic == "DAT":
                is_immediate = False
                current_pc += 1
            else:
                if mnemonic in ["JMP", "JNZ", "JIZ", "CLL", "LDI", "HRT", "IO"]:
                    is_immediate = False
                else:
                    is_immediate = arg_str.startswith("!")

                if is_immediate:
                    current_pc += 2  
                else:
                    current_pc += 1  

            cleaned_instructions.append((mnemonic, arg_str, is_immediate))

        # --- PASS 2: Compile to Binary Targets ---
        binary_words = []
        for mnemonic, arg_str, is_immediate in cleaned_instructions:
            if mnemonic == "DAT":
                val, _ = self.parse_token(arg_str)
                binary_words.append(val & 0xFFFF)
                continue

            if mnemonic not in self.opcodes:
                print(f"Error: Unknown mnemonic '{mnemonic}'")
                return None

            opcode = self.opcodes[mnemonic]
            arg_val = 0

            if arg_str:
                try:
                    arg_val, _ = self.parse_token(arg_str)
                except ValueError:
                    print(f"Error: Could not parse token or find label '{arg_str}'")
                    return None

            if is_immediate:
                ldi_word = (0x1 << 12) | (arg_val & 0x0FFF)
                binary_words.append(ldi_word)
                op_word = (opcode << 12) | 0x000
                binary_words.append(op_word)
            else:
                op_word = (opcode << 12) | (arg_val & 0x0FFF)
                binary_words.append(op_word)

        return binary_words

    def write_bin_file(self, binary_words, output_filepath):
        """
        Splits 16-bit words into High Byte and Low Byte 
        and writes them sequentially to a clean .bin file.
        """
        try:
            with open(output_filepath, "wb") as f:
                for word in binary_words:
                    high_byte = (word >> 8) & 0xFF
                    low_byte = word & 0xFF
                    f.write(bytes([high_byte, low_byte]))
            print(f"\n[Success] Binary saved to: {output_filepath}")
            print(f"Total size: {len(binary_words) * 2} bytes ({len(binary_words)} words).")
        except Exception as e:
            print(f"Error saving file: {e}")


# --- Script CLI Interface ---
if __name__ == "__main__":
    compiler = PulsarAssembler()
    
    # Quick configuration
    input_path = input("Enter assembly file path (.txt or .asm) > ").strip()
    
    if os.path.exists(input_path):
        with open(input_path, "r") as f:
            asm_code = f.read()
            
        print("Assembling source code...")
        words = compiler.assemble(asm_code)
        
        if words:
            # Print a quick preview array to terminal
            print("\nGenerated Machine Code Preview:")
            for i, w in enumerate(words):
                print(f"Word {i:02d}: {w:04X}")
                
            # Auto-generate output filename string (swaps extension for .bin)
            output_path = os.path.splitext(input_path)[0] + ".bin"
            compiler.write_bin_file(words, output_path)
    else:
        print(f"Error: Path '{input_path}' does not exist.")