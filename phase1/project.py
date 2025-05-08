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
    return 3  

def pass1(input_file, out_pass_file, symtab_file):
    symbol_table = {}
    lines = []

    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    
    first_line = lines[0].strip()
    parts = first_line.split()
    locctr = 0
    if len(parts) >= 3 and parts[1].upper() == 'START':
        locctr = int(parts[2], 16)
        symbol_table[parts[0]] = locctr  

    
    with open(out_pass_file, 'w') as out_pass:
        
        out_pass.write(f"\t{first_line}\n")

        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            label, opcode, operand = '', '', ''
            if len(parts) == 3:
                label, opcode, operand = parts
            elif len(parts) == 2:
                opcode, operand = parts
            elif len(parts) == 1:
                opcode = parts[0]

            
            if label:
                if label in symbol_table:
                    print(f"⚠️ Duplicate label: {label}")
                else:
                    symbol_table[label] = locctr

            
            out_pass.write(f"{locctr:04X}\t{line}\n")

            
            locctr += get_size(opcode.upper(), operand.upper() if operand else '')

    
    with open(symtab_file, 'w') as symtab:
        for label, address in symbol_table.items():
            symtab.write(f"{label}\t{address:04X}\n")



pass1('intermediate.txt', 'out_pass1.txt', 'symbTable.txt')



OPCODE_TABLE = {
    'LDA': '00', 'STA': '0C', 'LDX': '04', 'STX': '10',
    'ADD': '18', 'SUB': '1C', 'MUL': '20', 'DIV': '24',
    'COMP': '28', 'J': '3C', 'JEQ': '30', 'JGT': '34',
    'JLT': '38', 'JSUB': '48', 'RSUB': '4C', 'TIX': '2C',
    'LDCH': '50', 'STCH': '54'
}

def load_symtab(symtab_file):
    symtab = {}
    with open(symtab_file, 'r') as f:
        for line in f:
            label, addr = line.strip().split()
            symtab[label] = addr
    return symtab


def pass2(intermediate_file, symtab_file, out_pass2_file, htme_file):
    symtab = load_symtab(symtab_file)
    object_codes = []
    program_name = 'DEFAULT'
    start_address = None
    last_address = None

    with open(intermediate_file, 'r') as infile, open(out_pass2_file, 'w') as outfile:
        for line in infile:
            if not line.strip():
                continue

            if line[0].isspace():
                
                parts = line.strip().split()
                if len(parts) >= 3 and parts[1].upper() == 'START':
                    program_name = parts[0]
                    start_address = int(parts[2], 16)
                    outfile.write(f"\t{line.strip()}\n")
                continue

            locctr = line[:4]
            last_address = int(locctr, 16)
            parts = line[5:].strip().split()

            label, opcode, operand = '', '', ''
            if len(parts) == 3:
                label, opcode, operand = parts
            elif len(parts) == 2:
                opcode, operand = parts
            elif len(parts) == 1:
                opcode = parts[0]

            objcode = ''

            if opcode in OPCODE_TABLE:
                op_hex = OPCODE_TABLE[opcode]
                if opcode == 'RSUB':
                    objcode = op_hex + '0000'
                else:
                    addr = symtab.get(operand, '0000')
                    objcode = op_hex + addr.zfill(4)
            elif opcode == 'WORD':
                objcode = hex(int(operand))[2:].zfill(6).upper()
            elif opcode == 'BYTE':
                if operand.startswith("C'"):
                    chars = operand[2:-1]
                    objcode = ''.join([hex(ord(c))[2:].upper().zfill(2) for c in chars])
                elif operand.startswith("X'"):
                    objcode = operand[2:-1].upper()
            elif opcode in ['RESW', 'RESB']:
                objcode = ''

            outfile.write(f"{locctr}\t{line[5:].strip():<30}\t{objcode}\n")
            if objcode:
                object_codes.append((locctr, objcode))

    
    program_length = last_address - start_address if start_address is not None else 0

    
    with open(htme_file, 'w') as htme:
        htme.write(f"H^{program_name}^{start_address:06X}^{program_length:06X}\n")

        
        current_record = ''
        current_start = ''
        for i, (addr, code) in enumerate(object_codes):
            if not current_record:
                current_start = addr
            if len(current_record + code) > 60:
                length = len(current_record) // 2
                htme.write(f"T^{current_start}^{length:02X}^{current_record}\n")
                current_record = code
                current_start = addr
            else:
                current_record += code
        if current_record:
            length = len(current_record) // 2
            htme.write(f"T^{current_start}^{length:02X}^{current_record}\n")

        htme.write(f"E^{start_address:06X}\n")




pass2('out_pass1.txt', 'symbTable.txt', 'out_pass2.txt', 'HTME.txt')

