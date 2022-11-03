from re import S
from tokenizer import Tokenizer

def formatNode(node, indent = ""):
    nextIndent = indent + "  "
    if type(node) is list:
        res = "["
        for item in node:
            res += f"\n{nextIndent}"
            res += formatNode(item, nextIndent) if type(item) in (list, dict) else str(item)
        
        return res + f"\n{indent}]"
    
    res = "{"
    for key, value in node.items():
        res += f"\n{nextIndent}"
        if key != "type": res += f"{key} : "
        res += formatNode(value, nextIndent) if type(value) in (list, dict) else str(value) 

    return res + "\n" + indent + "}"

class Parser:
    def __init__(self, fileContent):
        self.tokenizer = Tokenizer("{" + fileContent + "}\n") #It takes me half an hour to explain why the {...}\n is needed, don't bother asking
    
    def parse(self):
        self.lookahead = self.tokenizer.getNextToken()
        program = self.Program()
        print(formatNode(program))
        return program
    
    def Program(self):
        lines = []
        self.eat("openBlock")
        while self.lookahead["type"] != "closeBlock":
            if self.lookahead["type"] == "newline":
                self.eat("newline")
                continue
            
            latestExpr = self.Expression()["value"]
            if latestExpr["type"] == "ELSE-INSTR":
                if lines[-1]["type"] == "IF-INSTR": lines[-1]["else"] = latestExpr["block"]
                else: raise Exception("Unexpected \"ELSE\"")
            
            else: lines.append(latestExpr)
        self.eat("closeBlock")
        
        return {
            "type"  : "Program",
            "value" : lines
        }

    def Expression(self, eatNewline = True):
        if self.lookahead is None: raise Exception("Abrupt ending in Expression")
        value = self.Assignment() if self.lookahead["type"] == "WORD" else self.Instruction()
        self.canAppendElse = value["type"] == "IF-INSTR"
        if eatNewline and (self.lookahead is not None and self.lookahead["type"] != "closeBlock"): self.eat("newline")
        return {
            "type"  : "Expression",
            "value" : value
        }

    def Assignment(self):
        target = self.eat("WORD")
        self.eat("arrow")
        value = self.Operation()
        return {
            "type"   : "Assignment",
            "target" : target,
            "value"  : value
        }

    def Instruction(self):
        keyword = self.eat("KEYWORD")["value"]
        if keyword == "WRITE" : return self.WRITE()
        if keyword == "READ"  : return self.READ()
        if keyword == "IF"    : return self.IF()
        if keyword == "ELSE"  : return self.ELSE()
        if keyword == "FOR"   : return self.FOR()
        if keyword == "WHILE" : return self.WHILE()
        if keyword == "REPEAT": return self.REPEAT()
        raise Exception(f"Unrecognized Instruction {keyword}")

    def WRITE(self):
        return {
            "type"  : "WRITE-INSTR",
            "value" : self.eat("message") if self.lookahead["type"] == "message" else self.Operation()
        }

    def READ(self):
        return {
            "type"  : "READ-INSTR",
            "value" : self.List()["value"]
        }
    
    def IF(self):
        condition = self.Condition()
        thenKW = self.eat("KEYWORD")["value"]
        if thenKW != "THEN": raise Exception(f"Unexpected KEYWORD \"{thenKW}\", expected \"THEN\"")
        block = self.Block()["value"]
        
        return {
            "type"  : "IF-INSTR",
            "cond"  : condition,
            "block" : block
        }
    
    def ELSE(self):
        
        return {
            "type"  : "ELSE-INSTR",
            "block" : self.Block()["value"]
        }
    
    def FOR(self):
        pass

    def WHILE(self):
        pass

    def REPEAT(self):
        pass

    def List(self):
        wordList = []
        wordList.append(self.eat("WORD")["value"])
        while self.lookahead["type"] == ",":
            self.eat(",")
            wordList.append(self.eat("WORD")["value"])
        
        if len(wordList) == 1: wordList = wordList[0]
        return {
            "type" : "list",
            "value" : wordList
        }

    def Condition(self):
        cp1 = self.Identifier()
        comparisonOp = self.eat("comparison")
        cp2 = self.Identifier()
        return {
            "type"    : "Condition",
            "cp1"     : cp1,
            "operand" : comparisonOp,
            "cp2"     : cp2
        }

    def Block(self):
        lines = []
        token = {
            "type" : "Block",
        }

        if self.lookahead is None: raise Exception("Abrupt ending block")
        if self.lookahead["type"] != "openBlock": 
            token["value"] = self.Expression(eatNewline = False)["value"]
            return token

        token["value"] = self.Program()
        return token

    def Operation(self):
        token = {
            "type" : "Operation",
            "op1"  : self.Identifier(),
        }
        if self.lookahead is None or self.lookahead["type"] != "operand": return token["op1"]
        operand = self.eat("operand")
        op2 = self.Identifier()
        token["operand"] = operand
        token["op2"]     = op2
        return token

    def Identifier(self):
        if self.lookahead is None: raise Exception("Abrupt ending in Identifier")
        value = self.eat("NUMBER") if self.lookahead["type"] == "NUMBER" else self.eat("WORD")
        if value["type"] == "NUMBER": value["value"] = float(value["value"]) if "." in value["value"] else int(value["value"])
        return {
            "type"  : "Identifier",
            "isVar" : value["type"] == "WORD",
            "value" : value["value"]
        }

    def eat(self, tokenType):
        token = self.lookahead
        if token is None: raise Exception("Unexpected End Of Input")
        if tokenType != token["type"]: raise Exception(f"Expected \"{tokenType}\" but got \"{token['type']}\"")
        self.lookahead = self.tokenizer.getNextToken()
        return token