from tokenizer import Tokenizer

class Parser:
    def __init__(self, fileContent):
        self.tokenizer = Tokenizer(fileContent)
    
    def parse(self):
        self.lookahead = self.tokenizer.getNextToken()
        program = self.Program()
        return program
    
    def Program(self):
        content = []
        while self.lookahead is not None: content.append(self.Expression()["value"])
        
        return {
            "type"  : "Program",
            "value" : content
        }

    def Expression(self, mustNewline = True):
        if self.lookahead is None: raise Exception("Abrupt ending in Expression")
        value = self.Assignment() if self.lookahead["type"] == "WORD" else self.Instruction()
        if mustNewline: self.eat("newline")
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
        if self.lookahead["type"] != "indent": 
            token["value"] = self.Expression(mustNewline = False)["value"]
            return token
        
        while self.lookahead["type"] == "indent":
            self.eat("indent")
            lines.append(self.Expression(mustNewline = False)["value"])
        
        token["value"] = lines
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