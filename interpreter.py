# Module for handling simulation mode
from parser import Parser
import sys

runtime_vars = {}

def Instruction(token):
    return {
        "WRITE-INSTR"  : WriteInstruction,
        "READ-INSTR"   : ReadInstruction,
        "FOR-INSTR"    : ForInstruction,
        "IF-INSTR"     : IfInstruction,
        "WHILE-INSTR"  : WhileInstruction,
        "REPEAT-INSTR" : RepeatInstruction,
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

    def parse(self):
        return self.parser.parse(doPrint = self.dbgModeFlag)

    def build(self):
        self.AST = Block(self.parse())
        if self.dbgModeFlag: print("Build complete.")

    def run(self):
        self.AST.exec()
        if self.dbgModeFlag:
            print("Execution terminated successfully.")
            print(runtime_vars)
    
    def transpile(self):
        languages = Token("").languages.keys()
        while True:
            lang = input("Select language of choice: ")
            if lang in languages: break
            print("Language unavailable, your options are:\n\t%s\n\n" % '\n\t'.join(languages))
        
        fileContent = self.AST.transpile(lang, isStart = True)
        with open(f"./FILES/{sys.argv[1]}.{lang}", "w") as fd: fd.write(fileContent)
        if self.dbgModeFlag: print(f".{lang} file created successfully.")

class Token:
    def __init__(self, token):
        self.argumentize(token)
        self.languages = {
            "js" : self.transpileJs,
        }
    
    def argumentize(self, token):
        pass

    def exec(self):
        pass

    def transpile(self, lang, isStart = False): return self.languages[lang](isStart)

    def transpileJs(self, isStart = False):
        return ["(() => {\n", "\n})();"] if isStart else ""

class Block(Token):
    def argumentize(self, token):
        self.lines = [Assignment(expression) if expression["type"] == "Assignment" else Instruction(expression) for expression in token["value"]]

    def exec(self):
        for line in self.lines: line.exec()

    def transpileJs(self, isStart):
        boilerplate = super().transpileJs(isStart)
        text = "\t" + ";\n\t".join([line.transpileJs() for line in self.lines]) + ";"
        return f"{boilerplate[0]}{text}{boilerplate[1]}" if boilerplate else text

class Assignment(Token):
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
    def argumentize(self, token):
        self.value = distinguishIdOp(token["value"])
    
    def exec(self):
        print(self.value.exec())

    def transpileJs(self):
        return f"console.log({self.value.transpileJs()})"

class ReadInstruction(Token):
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
    def argumentize(self, token):
        self.assignment = Assignment(token["iters"])
        self.block = Block(token["block"])

    def exec(self):
        iters = self.assignment.exec()
        if iters < 0: raise RuntimeError(f"Cannot loop a negative number ({iters}) of times.")
        if type(iters) is not int: raise RuntimeError(f"Cannot loop a non-integer number ({iters}) of times.")
        for i in range(iters): self.block.exec()

class ConditionalInstruction(Token):
    def argumentize(self, token):
        self.condition = Condition(token["cond"])
        self.block = Block(token["block"])

class IfInstruction(ConditionalInstruction):
    def argumentize(self, token):
        super.argumentize(token)
        if "else" in token:
            self.elseBlock = Block(token["else"])
            self.exec = self.execElse

    def exec(self):
        if self.condition.exec(): self.block.exec()
    
    def execElse(self):
        if self.condition.exec(): self.block.exec()
        else: self.elseBlock.exec()

class WhileInstruction(ConditionalInstruction):
    def exec(self):
        while self.condition.exec(): self.block.exec()

class RepeatInstruction(ConditionalInstruction):
    def exec(self):
        while True:
            self.block.exec()
            if self.condition.exec(): break

class Operation(Token):
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
    def argumentize(self, token):
        self.value = token["value"]
        self.exec = self.execVar if token["isVar"] else self.execNum
        self.isMsg = not token["isVar"] and type(token["value"]) is str

    def execNum(self): return self.value
    def execVar(self):
        if self.value not in runtime_vars: raise RuntimeError(f"Undefined variable \"{self.value}\"")
        return runtime_vars[self.value]
    
    def transpileJs(self):
        return f"\"{self.value}\"" if self.isMsg else str(self.value)