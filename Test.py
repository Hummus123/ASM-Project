import re
"""""
parser = Parser("file")
parser.directives.print()
parser.directives.out("txt")
parser.words.print()
parser.words.out("txt")
parser.code.print()
parser.code.out("txt")
parser.code.out("mif")
"""""

class Parser:
    def __init__(self, file) :
        self.fileStr = file
        self.instructions = {"ADD":"0000", "SUB":"0001", "INC":"0010",
                             "DEC":"0011","XOR":"0100", "AND": "0101",
                             "OR": "0110", "CPY": "0111", "SHRA":"1000",
                             "SLLL": "1001", "SHRL": "1001", "RLC": "1010",
                             "RRC": "1010", "LD": "1011", "ST": "1100",
                             "JUMP": "1101", "IN": "1110", "POP": "1110",
                             "OUT": "1111", "PUSH": "1111",
                             "C":"1000", "N":"0100", "V":"0010", "Z":"0001"}
        self.word = self.words
        with open(self.fileStr, "r") as toParse:
            toParse = toParse.read()
            self.Parsed = self.Parse(toParse)
            

    def Parse(self, info):
        keyWords = ["@start", "@end",".directives", ".enddirectives", ".word", ".equ", ".endconstants"]
        Spec = [
            ("END", r';'),
            ("COMMENT", r';.*')
            ("JA", r'@.+\b'),
            ("REG", r'R[0123]'),
            ("INSTRUCTION", r'[A-Za-z]+ ')
            ("MACRO", r'\..*;'),
            ("SKIP", r'[ \t]+'),
            ("NEWLINE", r'\n'),
            ("UNKOWN", r'.')
        ]
        regEx = "|".join('(?P<%s>%s)' % pair for pair in Spec)
        
    
    class words:
        def __init__(self, words = []) :
            self.words = words

        def __getitem__(self, index) :
            return self.words[index]
    
        def print(self) :
            for word in self.words:
                print(f"{word[0]}\t{word[1]}\t{word[2]}\n")

        def out(self, fileType = "txt") :
            if fileType == "txt":
                with open("words.txt", "w") as f:
                    for word in self.words:
                        f.write(f"{word[0]}\t{word[1]}\t{word[2]}\n")

        def addWord(self, lineNum, name, value):
            self.words.append((lineNum, name, value))


    class directives:
        def __init__(self, directives = []) :
            self.directives = directives

        def __getitem__(self, index) :
            return self.directives[index]
        
        def print(self) :
            for directive in self.directives:
                print(f"{directive[0]}\t{directive[1]}\t{directive[2]}\n")

        def out(self, fileType = "txt") :
            if fileType == "txt":
                with open("directives.txt", "w") as f:
                    for directive in self.directives:
                        f.write(f"{directive[0]}\t{directive[1]}\t{directive[2]}\n")

        def addDirective(self, lineNum, name, value):
            self.Directive.append((lineNum, name, value))
    
    class code:
        def __init__(self, code = []):
            self.code = code

        def __getitem__(self, index):
            return self.code[index]
        
        def print(self):
            for code in self.code:
                print(f"{code[0]}")
        
        def out(self, fileType = "mif"):
            
        def addCode(self, lineNum, type, args):
            self.code.append((lineNum, type, args))
    
