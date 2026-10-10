An investigation into making my own CPU design. The aim? Build a Forth interpreter to run on the custom CPU using whatever it takes. The CPU is done now I judt need to get my assembler into a proper transpiler.

to add:
- dat system ie variables DONE
- a way to read numbers in base 10 rather than 16: ` prefix DONE
- function system, custom call stack DONE

then i can make a FORTH INTERPRETER

SPECS:
1 core. idk clock speed
16 instructions
4096 16bit addresses of ram ie 8192 bytes

shoudl be possibl right?

V1: the CPU + m first attempt at an assembler
V2: same CPU, assembler now supports denary and dats
V3: changed instruction set, rewrote assembler from ground up