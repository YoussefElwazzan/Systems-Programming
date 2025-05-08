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



