def clean_assembly_code(input_file,output_file):
# Read the assembly code from the input file and write it to the output file with no comments and number lines
    with open (input_file,'r') as input , open(output_file,'w') as output:
        for line in input: 
            
            if ';' in line :
                line = line.split(';')[0]

            line = line.strip()

            if not line :
                continue

            parts = line.split(maxsplit=1)
            if len(parts) == 2 and parts[0].isdigit() :
                line = parts[1]

            output.write(line + '\n')


clean_assembly_code('in.txt','intermediate.txt')

def get_size(opcode, operand=''):
    if opcode == 'WORD':
        return 3
    elif opcode == 'RESW':
        return 3 * int(operand)
    elif opcode == 'RESB':
        return int(operand)
    elif opcode == 'BYTE':
        if operand.startswith("C'") and operand.endswith("'"):
            return len(operand[2:-1])
        elif operand.startswith("X'") and operand.endswith("'"):
            return len(operand[2:-1]) // 2
    return 3  # default size for normal instructions

def pass1(input_file, out_pass_file, symtab_file):
    locctr = 0
    symbol_table = {}
    start_found = False

    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    with open(out_pass_file, 'w') as out_pass:
        for index, line in enumerate(lines):
            parts = line.strip().split()

            if not parts:
                continue

            # Handle START directive
            if not start_found and len(parts) >= 2 and parts[1].upper() == 'START':
                start_found = True
                label = parts[0]
                locctr = int(parts[2], 16)
                symbol_table[label] = locctr
                out_pass.write(f"{locctr:04X}\t{line}")
                continue

            label, opcode, operand = '', '', ''
            if len(parts) == 3:
                label, opcode, operand = parts
            elif len(parts) == 2:
                opcode, operand = parts
            elif len(parts) == 1:
                opcode = parts[0]

            # Save label if exists
            if label:
                if label in symbol_table:
                    print(f"Duplicate label found: {label}")
                else:
                    symbol_table[label] = locctr

            # Write LOCCTR and line
            out_pass.write(f"{locctr:04X}\t{line}")

            # Update LOCCTR
            locctr += get_size(opcode.upper(), operand.upper() if operand else '')

    # Write symbol table to file
    with open(symtab_file, 'w') as symtab:
        for label, address in symbol_table.items():
            symtab.write(f"{label}\t{address:04X}\n")

pass1('intermediate.txt', 'out_pass1.txt', 'symbTable.txt')




