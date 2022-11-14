# Module for handling simulation mode
from parser import Parser

runtime_vars = {}

def Instruction(token):
    return {
        "WRITE-INSTR" : WriteInstruction,
        "READ-INSTR"  : ReadInstruction,
        "FOR-INSTR"   : ForInstruction,
        "IF-INSTR"    : IfInstruction,
    }[token["type"]](token)

def distinguishIdOp(token): return Operation(token) if token["type"] == "Operation" else Identifier(token)

def defineVariable(varName, value):
    runtime_vars[varName] = value

class Interpreter:
    def __init__(self, fileContent, toggle_dbgMode = False):
        self.dbgModeFlag = toggle_dbgMode
        self.parser = Parser(fileContent)
    
    def exec(self):
        self.build()
        self.run()

    def parse(self, doPrint=False):
        return self.parser.parse(doPrint)

    def build(self):
        self.AST = Block(self.parse(doPrint=True))
        if self.dbgModeFlag: print("Build complete.")

    def run(self):
        self.AST.exec()
        if self.dbgModeFlag: print("Execution terminated successfully.")
        #print(runtime_vars)

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
        self.lines = [Assignment(expression) if expression["type"] == "Assignment" else Instruction(expression) for expression in token["value"]]

    def exec(self):
        for line in self.lines: line.exec()

class Assignment(Token):
    def __init__(self, token): super().__init__(token)
    
    def argumentize(self, token):
        self.target = token["target"]
        self.value = distinguishIdOp(token["value"])
    
    def exec(self):
        value = self.value.exec()
        if type(value) is tuple:
            defineVariable(self.target, value[0])
            value = value[1]
        else: defineVariable(self.target, value)
        return value

class WriteInstruction(Token):
    def __init__(self, token): super().__init__(token)

    def argumentize(self, token):
        self.value = distinguishIdOp(token["value"])
    
    def exec(self):
        print(self.value.exec())

class ReadInstruction(Token):
    def __init__(self, token): super().__init__(token)

    def argumentize(self, token):
        value = token["value"]
        if type(value) is str:
            self.value = value
            return
        
        self.value = value.copy()
        if len(self.value) != len(set(self.value)): raise Exception(f"List of input values \"{', '.join(self.value)}\" contains duplicate names.")
    
    def exec(self):
        for name in self.value:
            value = input(f"Program requested value for variable \"{name}\": ")
            try: value = float(value) if "." in value else int(value)
            except ValueError: raise RuntimeError("Cannot input non-numeric value for variables.") from None
            defineVariable(name, value)

class ForInstruction(Token):
    def __init__(self, token): super().__init__(token)

    def argumentize(self, token):
        self.assignment = Assignment(token["iters"])
        self.block = Block(token["block"])

    def exec(self):
        iters = self.assignment.exec()
        if iters < 0: raise RuntimeError(f"Cannot loop a negative number ({iters}) of times.")
        if type(iters) is not int: raise RuntimeError(f"Cannot loop a non-integer number ({iters}) of times.")
        for i in range(iters): self.block.exec()

class IfInstruction(Token):
    def __init__(self, token): super().__init__(token)

    def argumentize(self, token):
        self.condition = Condition(token["cond"])
        self.block = Block(token["block"])
        if "else" in token:
            self.elseBlock = Block(token["else"])
            self.exec = self.execElse

    def exec(self):
        if self.condition.exec(): self.block.exec()
    
    def execElse(self):
        if self.condition.exec(): self.block.exec()
        else: self.elseBlock.exec()

class Operation(Token):
    def __init__(self, token): super().__init__(token)

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
            "TO"  : self.execTo,
        })[token["operand"]]
    
    def execAdd(self): return self.op1.exec() +  self.op2.exec()
    def execSub(self): return self.op1.exec() -  self.op2.exec()
    def execMul(self): return self.op1.exec() *  self.op2.exec()
    def execDiv(self): return self.op1.exec() /  self.op2.exec()
    def execPow(self): return self.op1.exec() ** self.op2.exec()
    def execMod(self): return self.op1.exec() %  self.op2.exec()
    def execTo(self) :
        op1 = self.op1.exec()
        op2 = self.op2.exec()
        return op1, op2 - op1

class Condition(Token):
    def __init__(self, token): super().__init__(token)

    def argumentize(self, token):
        self.cp1 = distinguishIdOp(token["cp1"])
        self.cp2 = distinguishIdOp(token["cp2"])
        self.exec = ({
            "<"  : self.execLst,
            "<=" : self.execLet,
            "="  : self.execEqs,
            ">"  : self.execGrt,
            ">=" : self.execGet,
            "!=" : self.execNeq,
        })[token["operand"]]
    
    def execLst(self): return self.cp1.exec() <  self.cp2.exec()
    def execLet(self): return self.cp1.exec() <= self.cp2.exec()
    def execEqs(self): return self.cp1.exec() == self.cp2.exec()
    def execGrt(self): return self.cp1.exec() >  self.cp2.exec()
    def execGet(self): return self.cp1.exec() >= self.cp2.exec()
    def execNeq(self): return self.cp1.exec() != self.cp2.exec()

class Identifier(Token):
    def __init__(self, token): super().__init__(token)

    def argumentize(self, token):
        self.value = token["value"]
        self.exec = self.execVar if token["isVar"] else self.execNum
    
    def execNum(self): return self.value
    def execVar(self):
        if self.value not in runtime_vars: raise RuntimeError(f"Undefined variable \"{self.value}\"")
        return runtime_vars[self.value]