import re
from typing import NamedTuple

class Parser:
    def __init__(self, file) :
        self.fileStr = file
        self.registers = {"R3":"11", "R2":"10", "R1":"01", "R0":"00"}
        self.instructions = {"ADD":"0000", "SUB":"0001", "INC":"0010",
                             "DEC":"0011","XOR":"0100", "AND": "0101",
                             "OR": "0110", "CPY": "0111", "SHRA":"1000",
                             "SHRL": "1001", "RLC": "1010",
                             "RRC": "1010", "LD": "1011", "ST": "1100",
                             "JUMP": "1101", "POP": "1110",
                             "PUSH": "1111",
                             "C":"1000", "N":"0100", "V":"0010", "Z":"0001", "U": "0000"}
        """""
        self.instructions = {"ADD":"0000", "SUB":"0001", "INC":"0010",
                             "DEC":"0011","XOR":"0100", "AND": "0101",
                             "OR": "0110", "CPY": "0111", "SHRA":"1000",
                             "SLLL": "1001", "SHRL": "1001", "RLC": "1010",
                             "RRC": "1010", "LD": "1011", "ST": "1100",
                             "JUMP": "1101", "IN": "1110",
                             "OUT": "1111",
                             "C":"1000", "N":"0100", "V":"0010", "Z":"0001", "U": "0000"}
        """""
        self.keyWords = [".directives", ".enddirectives", ".word", ".equ", ".endconstants"]
        self.ja = []
        self.words = self._words()
        self.directives = self._directives()
        self.code = self._code(self.instructions, self.registers, jumpaddr=self.ja)
        with open(self.fileStr, "r") as toParse:
            toParse = toParse.read()
            self.Parse(toParse)
            

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
                    if(previous.lastgroup != "MACRO" and previous.group() != "JUMP"):
                        raise Exception(f"Unkown Instruction ({str(linenum)}) {i.group()}")
            else:
                type = i.group()

            tokens.append(token(val, type, linenum))
            previous = i
        progbarlen = 20
        progressBar = ["\033[91m-\033[00m" for i in range(progbarlen)]
        for i in range(len(tokens)):
            progressBar[int(i/len(tokens) * progbarlen)] = "\033[92m-\033[00m"
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
                                if (t.val != "END"): raise Exception(f"Expected (;) at ({t.linenum})")

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
                                if (t.val != "END"): raise Exception(f"Expected (;) at ({t.linenum})")
                line = 0
                if (t.type.lower() == ".code"):
                    while (t.type.lower() != ".endcode"):
                        i += 1
                        t = tokens[i]
                        if (t.val == "JA"):
                            self.ja.append((line, t, tokens[i+1].type))
                        if (t.val == "INSTRUCTION"):
                            args = []
                            instruction = tokens[i]
                            i += 1
                            args.append(tokens[i])
                            if (instruction.type not in ["PUSH", "POP"]):
                                i += 1
                                args.append(tokens[i])
                            self.code.addCode(line, instruction, args)
                            i += 1
                            t = tokens[i]
                            if (t.val != "END"): raise Exception(f"Expected (;) at ({t.linenum})")
                            line += 1
                            if instruction.type in ["ST", "LD", "JUMP"]:
                                line+=1
                        
                        
                        
                        
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
        def __init__(self, instructions, registers, code = [], jumpaddr = []):
            self.code = code
            self.instructions = instructions
            self.registers = registers
            self.jas = jumpaddr

        def __getitem__(self, index):
            return self.code[index]
        
        def print(self):
            print("Code:")
            for code in self.code:
                print(code)
                print(f"\t{code[0]} {code[1]} {code[2]}\n")
        
        def out(self, fileType = "mif", depth = 1024, width = 8, addRad = "hex", datRad = "bin"):
            if fileType == "txt":
                with open("code.txt", "w") as f:
                    for code in self.code:
                        f.write(f"{code[0]} {code[1]} {code[2]}\n")
            elif fileType == "mif":
                with open("code.mif", "w") as f:
                    f.write(f"DEPTH = {depth};\nWIDTH = {width};\nADDRESS_RADIX = {addRad.upper()};\nDATA_RADIX = {datRad.upper()};\nCONTENT BEGIN\n")
                    linenumAdj = 0
                    for code in self.code:
                        linenumhex = ("0" * (4-len(hex(linenumAdj)[2:])) + hex(linenumAdj)[2:])
                        f.write(f"{linenumhex} : {self.instructions[code[1].type]}")
                        
                        if code[1].type == "JUMP":
                            binsum = "0000"
                            for l in code[2][0].type:
                                if l.upper() not in self.instructions:
                                    raise Exception(f"Unkown Jump Condition ({code.linenum})")
                                binsum = bin(int(self.instructions[l.upper()], 2) + int(binsum, 2))[2:]
                            binsumext = "".join(["0" for i in range(4-len(binsum))]) + binsum
                            f.write(f"{binsumext}; % JUMP {code[2][0].type} %\n")
                            if code[2][1].type not in [i[1].type for i in self.jas]:
                                print(code)
                                raise Exception(f"Jump Address not previously declared ({code[1].linenum})")
                            else:
                                linenumAdj += 1
                                desired = self.jas[[i[1].type for i in self.jas].index(code[2][1].type)]
                                offset = desired[0] - linenumAdj

                                if offset < 0:
                                    binoffset = bin(offset+1)
                                    binoffset = "".join(["0" for i in range(8-len(binoffset[3:]))]) + binoffset[3:]
                                    binoffset = "".join([{"0":"1", "1":"0"}[i] for i in binoffset])
                                else:
                                    binoffset = bin(offset)
                                    binoffset = "".join(["0" for i in range(8-len(binoffset[2:]))]) + binoffset[2:]
                                linenumhex = ("0" * (4-len(hex(linenumAdj)[2:])) + hex(linenumAdj)[2:])
                                f.write(f"{linenumhex} : {binoffset}; % Offset {offset} %\n")
                                linenumAdj += 1
                                continue
                        
                        if code[1].type in ["ST", "LD"]:
                            for arg in code[2]:
                                if arg.val == "REG":
                                    f.write(self.registers[arg.type])
                                if arg.val == "MEMADDRESS":
                                    spec = [("REG", r'R[0123]'), ("HEX", r'0x[0-9A-F]*')]
                                    regEx = "|".join('(?P<%s>%s)' % pair for pair in spec)
                                    match = re.findall(regEx, arg.type)
                                    hexaddr = bin(int(match[1][1], 16))[2:]
                                    if len(hexaddr) > 8:
                                        hexaddr = hexaddr[-8:]
                                    else:
                                        hexaddr = "".join(["0" for i in range(8-len(hexaddr))]) + hexaddr
                                    f.write(f"{self.registers[match[0][0]]};%{code[1].type}%\n")
                                    linenumAdj += 1
                                    linenumhex = ("0" * (4-len(hex(linenumAdj)[2:])) + hex(linenumAdj)[2:])
                                    f.write(f"{linenumhex} : {hexaddr}")

                        else:
                            for arg in code[2]:
                                if arg.val == "REG":
                                    f.write(self.registers[arg.type])
                                    if code[1].type in ["POP", "PUSH"]:
                                        f.write("00")
                                elif arg.val == "CONST":
                                    k = bin(int(arg.type))[2:]
                                    if len(k) < 2:
                                        k = "0" + k
                                    f.write(k)
                                
                        linenumAdj += 1
                        f.write(";\n")
                    f.write(f"[ {hex(linenumAdj)[2:]} .. 3FF ] : 00000000;\n END;")
        def addCode(self, lineNum, type, args):
            self.code.append((lineNum, type, args))
        
        def addJA(self, ja):
            self.jas.append(ja)
    
test = Parser("testfile4.txt")

if __name__ == "main":
    test.words.out()
    test.code.out()
    test.directives.out()

test.words.out()
test.code.out()
test.directives.out("txt")