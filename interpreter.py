# Module for handling simulation mode
from parser import Parser

runtime_vars = {}
class Interpreter:
    def __init__(self, fileContent, toggle_dbgMode = False):
        self.dbgModeFlag = toggle_dbgMode
        self.parser   = Parser(fileContent)
    
    def exec(self):
        self.build()
        self.run()

    def parse(self, doPrint=False):
        return self.parser.parse(doPrint)

    def build(self):
        self.AST = Block(self.parse())
        if self.dbgModeFlag: print("Build complete.")

    def run(self):
        self.AST.exec()
        if self.dbgModeFlag: print("Execution terminated successfully.")
        print(runtime_vars)

class Token:
    def __init__(self, token):
        self.argumentize(token)
    
    def argumentize(self, token):
        pass

    def exec(self):
        pass

class Block(Token):
    def __init__(self, token): super().__init__(token)

    def argumentize(self, token):
        self.expressions = [Assignment(expression) if expression["type"] == "Assignment" else Instruction(expression) for expression in token["value"]]

    def exec(self):
        for expression in self.expressions: expression.exec()

class Assignment(Token):
    def __init__(self, token): super().__init__(token)
    
    def argumentize(self, token):
        self.target = token["target"]
        self.value = Operation(token["value"]) if token["value"]["type"] == "Operation" else Identifier(token["value"])
    
    def exec(self):
        runtime_vars[self.target] = self.value.exec()

class Instruction(Token):
    def __init__(self, token): super().__init__(token)

class Operation(Token):
    def __init__(self, token):
        super().__init__(token)

    def argumentize(self, token):
        self.op1 = Identifier(token["op1"])
        self.op2 = Identifier(token["op2"])
        self.exec = ({
            "+"   : self.execAdd,
            "-"   : self.execSub,
            "*"   : self.execMul,
            "/"   : self.execDiv,
            "^"   : self.execPow,
            "MOD" : self.execMod,
        })[token["operand"]]
    
    def execAdd(self): return self.op1.exec() +  self.op2.exec()
    def execSub(self): return self.op1.exec() -  self.op2.exec()
    def execMul(self): return self.op1.exec() *  self.op2.exec()
    def execDiv(self): return self.op1.exec() /  self.op2.exec()
    def execPow(self): return self.op1.exec() ** self.op2.exec()
    def execMod(self): return self.op1.exec() %  self.op2.exec()

class Identifier(Token):
    def __init__(self, token): super().__init__(token)

    def argumentize(self, token):
        self.value = token["value"]
        self.exec = self.execVar if token["isVar"] else self.execNum
    
    def execNum(self): return self.value
    def execVar(self):
        if self.value not in runtime_vars: raise RuntimeError(f"Undefined variable \"{self.value}\"")
        return runtime_vars[self.value]