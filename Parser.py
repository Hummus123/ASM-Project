import re
from typing import NamedTuple

class Parser:
    def __init__(self, file) :
        self.fileStr = file
        self.registers = {"R3":"11", "R2":"10", "R1":"01", "R0":"00"}
        self.instructions = {"ADD":"0000", "SUB":"0001", "INC":"0010",
                             "DEC":"0011","XOR":"0100", "AND": "0101",
                             "OR": "0110", "CPY": "0111", "SHRA":"1000",
                             "SLLL": "1001", "SHRL": "1001", "RLC": "1010",
                             "RRC": "1010", "LD": "1011", "ST": "1100",
                             "JUMP": "1101", "IN": "1110", "POP": "1110",
                             "OUT": "1111", "PUSH": "1111",
                             "C":"1000", "N":"0100", "V":"0010", "Z":"0001", "U": " "}
        self.keyWords = [".directives", ".enddirectives", ".word", ".equ", ".endconstants"]
        self.ja = []
        self.words = self._words()
        self.directives = self._directives()
        self.code = self._code(self.instructions, self.registers)
        with open(self.fileStr, "r") as toParse:
            toParse = toParse.read()
            self.Parsed = self.Parse(toParse)
            

    def Parse(self, f):
        linecount = f.count("\n")
        Spec = [
            ("END", r';.*'),
            ("JA", r'\@[a-zA-Z0-9]+'),
            ("REG", r'R[0123]'),
            ("MEMADDRESS", r'[mM]\[.+?\]'),
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
                if (instruction not in self.instructions):
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
            if (i % 15 == 0):
                print(f"{i/len(tokens)*100:.1f}%\t", end = "")
                print("".join(progressBar),)

            t = tokens[i]
            if (t.val == "MACRO"):
                if (t.type.lower() == ".directives"):
                    while (t.type.lower() != ".enddirectives"):
                        i += 1
                        t = tokens[i]
                        if (t.val == "MACRO"):
                            if t.type.lower() == ".equ":
                                i += 1
                                name = tokens[i]
                                i += 1
                                val = tokens[i]
                                self.directives.addDirective(name.linenum, name, val)
                                i += 1
                                t = tokens[i]
                                if (t.val != "END"): raise Exception(f"Expected ;, {t.linenum}")


                if(t.type.lower() == ".constants"):
                    while (t.type.lower() != ".endconstants"):
                        i += 1
                        t = tokens[i]
                        if (t.val == "MACRO"):
                            if t.type.lower() == ".word":
                                i += 1
                                name = tokens[i]
                                i += 1
                                val = tokens[i]
                                self.words.addWord(name.linenum, name, val)
                                i += 1
                                t = tokens[i]
                                if (t.val != "END"): raise Exception(f"Expected ;, {t.linenum}")
                
                if (t.type.lower() == ".code"):
                    while (t.type.lower() != ".endcode"):
                        i += 1
                        t = tokens[i]
                        if (t.val == "INSTRUCTION"):
                            args = []
                            instruction = tokens[i]
                            i += 1
                            args.append(tokens[i])
                            i += 1
                            args.append(tokens[i])
                            self.code.addCode(instruction.linenum, instruction, args)
                            i += 1
                            t = tokens[i]
                            if (t.val != "END"): raise Exception(f"Expected ;, {t.linenum}")
                        if (t.val == "JA"):
                            self.ja.append((t.linenum, t))

        print("\tDone!")
        
    
    class _words:
        def __init__(self, words = []) :
            self.words = words

        def __getitem__(self, index) :
            return self.words[index]
    
        def print(self) :
            print("Words:")
            for word in self.words:
                print(f"\t{word[0]} {word[1]} {word[2]}\n")

        def out(self, fileType = "txt") :
            if fileType == "txt":
                with open("words.txt", "w") as f:
                    for word in self.words:
                        f.write(f"{word[0]} {word[1]} {word[2]}\n")

        def addWord(self, lineNum, name, value):
            self.words.append((lineNum, name, value))


    class _directives:
        def __init__(self, directives = []) :
            self.directives = directives

        def __getitem__(self, index) :
            return self.directives[index]
        
        def print(self) :
            print("Directives:")
            for directive in self.directives:
                print(f"\t{directive[0]} {directive[1]} {directive[2]}\n")

        def out(self, fileType = "txt") :
            if fileType == "txt":
                with open("directives.txt", "w") as f:
                    for directive in self.directives:
                        f.write(f"{directive[0]}\t{directive[1]}\t{directive[2]}\n")

        def addDirective(self, lineNum, name, value):
            self.directives.append((lineNum, name, value))
  
    class _code:
        def __init__(self, instructions, registers, code = []):
            self.code = code
            self.instructions = instructions
            self.registers = registers

        def __getitem__(self, index):
            return self.code[index]
        
        def print(self):
            print("Code:")
            for code in self.code:
                print(f"\t{code[0]} {code[1]} {code[2]}\n")
        
        def out(self, fileType = "mif", depth = 32, width = 8, addRad = "hex", datRad = "bin"):
            if fileType == "txt":
                with open("code.txt", "w") as f:
                    for code in self.code:
                        f.write(f"{code[0]} {code[1]} {code[2]}\n")
            elif fileType == "mif":
                with open("code.txt", "w") as f:
                    f.write(f"DEPTH = {depth};\nWIDTH = {width};\nADDRESS_RADIX = {addRad.upper()};\nDATA_RADIX = {datRad.upper()};\nCONTENT BEGIN\n")
                    linenumAdj = 0
                    for code in self.code:
                        f.write(f"{hex(linenumAdj)} : {self.instructions[code[1].type]}")
                        
                        if code[1].type == "JUMP":
                            f.write("jupman")
                        else:
                            for arg in code[2]:
                                if arg.val == "REG":
                                    f.write(self.registers[arg.type])
                                elif arg.val == "CONST":
                                    f.write(bin(int(arg.type))[2:])
                        linenumAdj += 1
                        f.write("\n")
        def addCode(self, lineNum, type, args):
            self.code.append((lineNum, type, args))
    
test = Parser("dxp_MUL_mmiop.txt")

test.directives.print()
test.words.print()
test.code.print()

test.words.out()
test.code.out()
test.directives.out()