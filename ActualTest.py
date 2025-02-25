import re
from typing import NamedTuple

with open("dxp_MUL_mmiop.txt", "r") as f:
    f = f.read()
    """""
    m = re.search(r';.* | \n;', f)
    while m != None:
        f = f[:m.start()] + f[m.end():]
        m = re.search(r';.*', f)
    m = re.search(r'\t|(    )|(^\s*$)',  f)
    while m != None:
        f = f[:m.start()] + f[m.end():]
        m = re.search(r'\t|(    )|(^\s*$)',  f)
    """""
    
    #print("\n" + f)
    linecount = f.count("\n")
    instructions = {"ADD":"0000", "SUB":"0001", "INC":"0010",
                    "DEC":"0011","XOR":"0100", "AND": "0101",
                    "OR": "0110", "CPY": "0111", "SHRA":"1000",
                    "SLLL": "1001", "SHRL": "1001", "RLC": "1010",
                    "RRC": "1010", "LD": "1011", "ST": "1100",
                    "JUMP": "1101", "IN": "1110", "POP": "1110",
                    "OUT": "1111", "PUSH": "1111",
                    "C":"1000", "N":"0100", "V":"0010", "Z":"0001", "U":" "}
    registers = {"R3":"11", "R2":"10", "R1":"01", "R0":"00"}
        
    keyWords = [".directives", ".enddirectives", ".word", ".equ", ".endconstants"]
    Spec = [
            ("END", r';.*'),
            ("JA", r'\@[a-zA-Z0-9]+'),
            ("REG", r'R[0123]'),
            ("MEMADDRESS", r'M\[[\w*\]'),
            ("MACRO", r'\.\w*'),
            ("INSTRUCTION", r'[A-Za-z]+'),
            ("HEX", r'0x[0-9A-F]*'),
            ("CONST", r'[0-3]'),
            ("SKIP", r'[ \t\,]+'),
            ("NEWLINE", r'\n'),
            ("UNKOWN", r'.')
        ]
    regEx = "|".join('(?P<%s>%s)' % pair for pair in Spec)

    class token(NamedTuple):
        val: str
        type: str
        linenum: int

    linenum = 1
    


    matches = re.finditer(regEx, f)
    tokens = []
    for i in matches:
        val = i.lastgroup
        if (val == "NEWLINE"):
            linenum += 1
            continue
        elif (val == "SKIP"):
            continue
        elif (val == "INSTRUCTION"):
            instruction = i.group()
            type = instruction
            if (instruction not in instructions):
                if(previous.lastgroup != "MACRO"):
                    raise Exception(f"Unkown Instruction ({str(linenum)}) {i.group()}")
                
        elif (val == "MACRO"):
            #print(i.group())
            type = i.group()
        else:
            type = i.group()

        tokens.append(token(val, type, linenum))
        previous = i
    
    macros = []
    progressBar = ["\033[91m-\033[00m" for i in range(20)]

    for i in range(len(tokens)):
        progressBar[int(i/len(tokens) * len(progressBar))] = "\033[92m-\033[00m"
        if (i % 10 == 0):
            print(f"{i/len(tokens)*100:.1f}% ", end = "")
            print("".join(progressBar),)

        t = tokens[i]
        if (t.val == "MACRO"):
            if(t.type.lower() == ".directives"):
                while (t.type.lower() != ".enddirectives"):
                    print(t)
                    i += 1
                    t = tokens[i]

            if(t.type.lower() == ".constants"):
                while (t.type.lower() != ".endconstants"):
                    print(t)
                    i += 1
                    t = tokens[i]
        if (t.val == "INSTRUCTION"):
            while(t.val != "END"):
                print(t)
                i += 1
                t = tokens[i]
            print()
    print("\tDone!")