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
        while self.lookahead is not None: content.append(self.Expression())
        
        return {
            "type"  : "Program",
            "value" : content
        }

    def Expression(self):
        if self.lookahead is None: raise Exception("Abrupt ending in Expression")
        firstToken = self.eat("WORD")
        value = self.Assignment(firstToken) if self.lookahead["type"] == "arrow" else self.Instruction(firstToken)
        self.eat("newline")
        return {
            "type"  : "Expression",
            "value" : value
        }

    def Assignment(self, firstToken):
        self.eat("arrow")
        value = self.Identifier() #incomplete!
        return {
            "type"   : "Assignment",
            "target" : firstToken,
            "value"  : value
        }

    def Instruction(self, firstToken):
        if self.lookahead is None: raise Exception("Abrupt ending in Instruction")
        if firstToken["value"] == "WRITE": return self.WRITE()
        raise Exception(f"Unrecognized Instruction {firstToken}")

    def WRITE(self):
        return {
            "type"  : "WRITE-INSTR",
            "value" : self.eat("message") #incomplete!
        }

    def Identifier(self):
        if self.lookahead is None: raise Exception("Abrupt ending in Identifier")
        value = self.eat("NUMBER") if self.lookahead["type"] == "NUMBER" else self.eat("WORD")
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