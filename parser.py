from tokenizer import Tokenizer

def formatNode(node, indent = ""):
    if type(node) not in (list, dict): return str(node)

    nextIndent = indent + "⋮ "
    res, iterator, ending = ("[", node, "]") if type(node) is list else ("{", node.items(), "}")
    
    for item in iterator:
        res += f"\n{nextIndent}"
        itemIsList = type(item) is tuple
        if itemIsList and item[0] != "type": res += f"{item[0]} : "
        res += formatNode(item[1] if itemIsList else item, nextIndent)

    return f"{res}\n{indent}{ending}"

class Parser:
    def __init__(self, fileContent):
        self.tokenizer = Tokenizer("{" + fileContent + "}\n") #It takes me half an hour to explain why the {...}\n is needed, don't bother asking
    
    def parse(self, doPrint=False):
        self.lookahead = self.tokenizer.getNextToken()
        program = self.Program()
        if doPrint: print(formatNode(program))
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
            
            elif latestExpr["type"] == "UNTIL-INSTR":
                if lines[-1]["type"] == "REPEAT-INSTR": lines[-1]["cond"] = latestExpr["cond"]
                else: raise Exception("Unexpected \"UNTIL\"")
            
            else: lines.append(latestExpr)
        self.eat("closeBlock")
        
        return {
            "type"  : "Program",
            "value" : lines
        }

    def Expression(self, eatNewline = True):
        if self.lookahead is None: raise Exception("Abrupt ending in Expression")
        value = self.Assignment() if self.lookahead["type"] == "WORD" else self.Instruction()
        if eatNewline and (self.lookahead is not None and self.lookahead["type"] != "closeBlock"): self.eat("newline")
        return {
            "type"  : "Expression",
            "value" : value
        }

    def Assignment(self):
        target = self.eat("WORD")["value"]
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
        if keyword == "UNTIL" : return self.UNTIL()
        raise Exception(f"Unrecognized Instruction {keyword}")

    def WRITE(self):
        return {
            "type"  : "WRITE-INSTR",
            "value" : self.Message() if self.lookahead["type"] == "message" else self.Operation()
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
        token = {
            "type"  : "IF-INSTR",
            "cond"  : condition,
            "block" : block
        }

        if self.lookahead and self.lookahead["type"] != "newline":
            self.eat("KEYWORD")
            token["else"] = self.ELSE()["block"]

        return token
    
    def ELSE(self):
        return {
            "type"  : "ELSE-INSTR",
            "block" : self.Block()["value"]
        }
    
    def FOR(self):
        iters = self.Assignment()
        doKW = self.eat("KEYWORD")["value"]
        if doKW != "DO": raise Exception(f"Unexpected KEYWORD \"{doKW}\", expected \"DO\"")
        return {
            "type"  : "FOR-INSTR",
            "iters" : iters,
            "block" : self.Block()["value"]
        }

    def WHILE(self):
        cond = self.Condition()
        doKW = self.eat("KEYWORD")["value"]
        if doKW != "DO": raise Exception(f"Unexpected KEYWORD \"{doKW}\", expected \"DO\"")
        return {
            "type"  : "WHILE-INSTR",
            "cond"  : cond,
            "block" : self.Block()["value"]
        }

    def REPEAT(self):
        block = self.Block()["value"]
        token = {
            "type"  : "REPEAT-INSTR",
            "block" : block
        }

        if self.lookahead and self.lookahead["type"] != "newline":
            self.eat("KEYWORD")
            token["cond"] = self.UNTIL()["cond"]

        return token

    def UNTIL(self):
        return {
            "type" : "UNTIL-INSTR",
            "cond" : self.Condition(),
        }

    def Message(self):
        return {
            "type"  : "Identifier",
            "isVar" : False,
            "value" : self.eat("message")["value"]
        }

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

    def Block(self): #Opted for the classic {...} syntax style for blocks cuz I couldn't be bothered to keep track of indentation. IDK why nor how python does it. 
        lines = []
        token = {
            "type" : "Block",
        }

        if self.lookahead is None: raise Exception("Abrupt ending block")
        if self.lookahead["type"] != "openBlock": 
            token["value"] = self.Expression(eatNewline = False)["value"]
            return token

        token["value"] = self.Program()["value"]
        return token

    def Operation(self):
        token = {
            "type" : "Operation",
            "op1"  : self.Identifier(),
        }
        if self.lookahead is None or self.lookahead["type"] != "operand": return token["op1"]
        operand = self.eat("operand")["value"]
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