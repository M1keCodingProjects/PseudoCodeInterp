# Module for handling simulation mode
from Parser import Parser
import sys

runtime_vars = {}
tabID = 0

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
        print("Build complete.")

    def run(self):
        global runtime_vars
        runtime_vars = {}
        self.AST.exec()
        print("Execution terminated successfully.")
        if self.dbgModeFlag: print(runtime_vars)
    
    def transpile(self):
        global runtime_vars, tabID
        runtime_vars = {}
        tabID = 0
        languages = Token("").languages.keys()
        while True:
            lang = input("Select language of choice: ")
            if lang in languages: break
            print("Language unavailable, your options are:\n\t%s\n\n" % '\n\t'.join(languages))
        
        fileContent = self.AST.transpile(lang, isStart = True)
        with open(f"./FILES/{sys.argv[1]}.{lang}", "w") as fd: fd.write(fileContent)
        print(f".{lang} file created successfully.")

class Token:
    def __init__(self, token):
        self.argumentize(token)
        self.languages = {
            "js"  : self.transpileJs,
            "py"  : self.transpilePy,
            "c"   : self.transpileC,
            "cpp" : self.transpileCpp,
            "gl"  : self.transpileGl,
        }
    
    def argumentize(self, token):
        pass

    def exec(self):
        pass

    def transpile(self, lang, isStart = False): return self.languages[lang](isStart)

    def transpileJs(self): return ["(() => {\n", "\n})();"]
    
    def transpilePy(self): return ["def main():\n", "\n\nif __name__ == '__main__': main()"]

    def transpileC(self): return ["#include<stdio.h>\n#include<cstdlib>\n\nint main() {\n", "\n}"]

    def transpileCpp(self): return ["#include<iostream>\n#include<cstdlib>\n\nusing namespace std;\n\nint main() {\n", "\n}"]

    def transpileGl(self): return "use std = \"std GLib\"\n\n"

class Block(Token):
    def argumentize(self, token):
        self.lines = [Assignment(expression) if expression["type"] == "Assignment" else Instruction(expression) for expression in token["value"]]

    def exec(self):
        for line in self.lines: line.exec()

    def transpileJs(self, isStart = False):
        if isStart: boilerplate = super().transpileJs()
        global tabID
        tabID += 1
        indent = tabID * "\t"
        text = indent + (";\n%s" % indent).join([line.transpileJs() for line in self.lines])
        if len(text.lstrip()) and text[-1] != "}": text += ";"
        tabID -= 1
        return f"{boilerplate[0]}{text}{boilerplate[1]}" if isStart else ("{\n%s\n%s}" % (text, indent[1:]))
    
    def transpilePy(self, isStart = False):
        if isStart: boilerplate = super().transpilePy()
        global tabID
        tabID += 1
        indent = tabID * "\t"
        text = indent + ("\n%s" % indent).join([line.transpilePy() for line in self.lines])
        tabID -= 1
        return f"{boilerplate[0]}{text}{boilerplate[1]}" if isStart else ("\n%s" % text)
    
    def transpileC(self, isStart = False):
        if isStart: boilerplate = super().transpileC()
        global tabID
        tabID += 1
        indent = tabID * "\t"
        text = indent + (";\n%s" % indent).join([line.transpileC() for line in self.lines])
        if len(text.lstrip()) and text[-1] != "}": text += ";"
        tabID -= 1
        return f"{boilerplate[0]}{text}{boilerplate[1]}" if isStart else ("{\n%s\n%s}" % (text, indent[1:]))
    
    def transpileCpp(self, isStart = False):
        if isStart: boilerplate = super().transpileCpp()
        global tabID
        tabID += 1
        indent = tabID * "\t"
        text = indent + (";\n%s" % indent).join([line.transpileCpp() for line in self.lines])
        if len(text.lstrip()) and text[-1] != "}": text += ";"
        tabID -= 1
        return f"{boilerplate[0]}{text}{boilerplate[1]}" if isStart else ("{\n%s\n%s}" % (text, indent[1:]))
    
    def transpileGl(self, isStart = False):
        global tabID
        if isStart:
            boilerplate = super().transpileGl()
            tabID -= 1
        tabID += 1
        indent = tabID * "\t"
        text = indent + ("\n%s" % indent).join([line.transpileGl() for line in self.lines])
        tabID -= 1
        return f"{boilerplate}{text}" if isStart else ("{\n%s\n%s}" % (text, indent[1:]))

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
    
    def transpileJs(self):
        target = ""
        if self.target not in runtime_vars:
            target = "var "
            runtime_vars[self.target] = "defined"
        value = self.value.transpileJs()
        target += f"{self.target} = "
        if type(value) is tuple:
            target += value[0]
            return target, value
        
        return f"{target}{value}"
    
    def transpilePy(self):
        value = self.value.transpilePy()
        target = f"{self.target} = "
        if type(value) is tuple:
            target += value[0]
            return target, value
        
        return f"{target}{value}"
    
    def transpileC(self):
        target = ""
        if self.target not in runtime_vars:
            target = "float "
            runtime_vars[self.target] = "defined"
        value = self.value.transpileC()
        target += f"{self.target} = "
        if type(value) is tuple:
            target += value[0]
            return target, value
        
        return f"{target}{value}"
    
    def transpileCpp(self):
        target = ""
        if self.target not in runtime_vars:
            target = "float "
            runtime_vars[self.target] = "defined"
        value = self.value.transpileCpp()
        target += f"{self.target} = "
        if type(value) is tuple:
            target += value[0]
            return target, value
        
        return f"{target}{value}"
    
    def transpileGl(self):
        target = ""
        if self.target not in runtime_vars:
            target = "make "
            runtime_vars[self.target] = "defined"
        value = self.value.transpileGl()
        target += f"{self.target} = "
        if type(value) is tuple:
            target += value[0]
            return target, value
        
        return f"{target}{value}"

class WriteInstruction(Token):
    def argumentize(self, token):
        self.value = distinguishIdOp(token["value"])
    
    def exec(self):
        print(self.value.exec())

    def transpileJs(self):
        return f"console.log({self.value.transpileJs()})"
    
    def transpilePy(self):
        return f"print({self.value.transpilePy()})"
    
    def transpileC(self):
        return f"printf(\"%f\", {self.value.transpileC()})"
    
    def transpileCpp(self):
        return f"cout << {self.value.transpileCpp()} << endl"
    
    def transpileGl(self):
        return f"print {self.value.transpileGl()}"

class ReadInstruction(Token):
    def argumentize(self, token):
        value = token["value"]
        if type(value) is str:
            self.value = [value]
            return
        
        self.value = value.copy()
        if len(self.value) != len(set(self.value)): raise Exception(f"List of input values \"{', '.join(self.value)}\" contains duplicate names.")
    
    def exec(self):
        for name in self.value:
            value = input(f"Program requested value for variable \"{name}\": ")
            try: value = float(value) if "." in value else int(value)
            except ValueError: raise RuntimeError("Cannot input non-numeric value for variables.") from None
            defineVariable(name, value)

    def transpileJs(self):
        values = []
        for name in self.value:
            values.append("")
            if name not in runtime_vars:
                values[-1] += "var "
                runtime_vars[name] = "defined"
            values[-1] += f"{name} = prompt('Program requested value for variable \"{name}\": ')"
        return (";\n" + "\t" * tabID).join(values)
    
    def transpilePy(self):
        values = []
        for name in self.value: values.append(f"{name} = float(input('Program requested value for variable \"{name}\": '))")
        return ("\n" + "\t" * tabID).join(values)
    
    def transpileC(self):
        values = []
        indent = tabID * "\t"
        for name in self.value:
            values.append("")
            if name not in runtime_vars:
                values[-1] += "float "
                runtime_vars[name] = "defined"
            values[-1] += f"{name};\n{indent}scanf(\"%f\", &{name})"
        return (";\n" + indent).join(values)
    
    def transpileCpp(self):
        values = []
        indent = tabID * "\t"
        for name in self.value:
            values.append("")
            if name not in runtime_vars:
                values[-1] += "float "
                runtime_vars[name] = "defined"
            values[-1] += f"{name};\n{indent}cin >> {name}"
        return (";\n" + indent).join(values)
    
    def transpileGl(self):
        values = []
        indent = tabID * "\t"
        for name in self.value:
            values.append("")
            if name not in runtime_vars:
                values[-1] += "make "
                runtime_vars[name] = "defined"
            values[-1] += f"{name} :num = inp"
        return ("\n" + indent).join(values)

class ForInstruction(Token):
    def argumentize(self, token):
        self.assignment = Assignment(token["iters"])
        self.block = Block(token["block"])

    def exec(self):
        iters = self.assignment.exec()
        if iters < 0: raise RuntimeError(f"Cannot loop a negative number ({iters}) of times.")
        if type(iters) is not int: raise RuntimeError(f"Cannot loop a non-integer number ({iters}) of times.")
        for i in range(iters): self.block.exec()

    def transpileJs(self):
        iterator = self.assignment.transpileJs()
        if type(iterator) is tuple:
            fromValue, toValue = iterator[1]
            iterator = iterator[0]
        else:
            fromValue = 0
            toValue = iterator[iterator.find("=") + 2:]

        return f"{iterator};\n" + "\t" * tabID + f"for(let _ = {fromValue}; _ < {toValue}; _++) {self.block.transpileJs()}"

    def transpilePy(self):
        iters = self.assignment.transpilePy()
        if type(iters) is tuple:
            iterLen = f"{iters[1][0]}, {iters[1][1]}"
            iters = iters[0]
        else: iterLen = iters[iters.find("=") + 2:]

        return "%s\n%sfor _ in range(%s):%s" % (iters, '\t' * tabID, iterLen, self.block.transpilePy())
    
    def transpileC(self):
        iterator = self.assignment.transpileC()
        if type(iterator) is tuple:
            fromValue, toValue = iterator[1]
            iterator = iterator[0]
        else:
            fromValue = 0
            toValue = iterator[iterator.find("=") + 2:]

        return f"{iterator};\n" + "\t" * tabID + f"for(int _ = {fromValue}; _ < {toValue}; _++) {self.block.transpileC()}"

    def transpileCpp(self):
        iterator = self.assignment.transpileCpp()
        if type(iterator) is tuple:
            fromValue, toValue = iterator[1]
            iterator = iterator[0]
        else:
            fromValue = 0
            toValue = iterator[iterator.find("=") + 2:]

        return f"{iterator};\n" + "\t" * tabID + f"for(int _ = {fromValue}; _ < {toValue}; _++) {self.block.transpileCpp()}"
    
    def transpileGl(self):
        iterator = self.assignment.transpileGl()
        if type(iterator) is tuple:
            fromValue, toValue = iterator[1]
            toValue += f" {fromValue} -"
            iterator = iterator[0]
        else:
            fromValue = 0
            toValue = iterator[iterator.find("=") + 2:]

        return f"{iterator}\n" + "\t" * tabID + f"loop {toValue} {self.block.transpileGl()}"

class ConditionalInstruction(Token):
    def argumentize(self, token):
        self.condition = Condition(token["cond"])
        self.block = Block(token["block"])

    def transpileJs(self):
        return "(%s) %s" % (self.condition.transpileJs(), self.block.transpileJs())
    
    def transpilePy(self):
        return "%s:%s" % (self.condition.transpilePy(), self.block.transpilePy())
    
    def transpileC(self):
        return "(%s) %s" % (self.condition.transpileC(), self.block.transpileC())
    
    def transpileCpp(self):
        return "(%s) %s" % (self.condition.transpileCpp(), self.block.transpileCpp())
    
    def transpileGl(self):
        return [self.condition.transpileGl(), self.block.transpileGl()]

class IfInstruction(ConditionalInstruction):
    def argumentize(self, token):
        super().argumentize(token)
        if "else" in token:
            self.elseBlock = Block(token["else"])
            self.exec = self.execElse

    def exec(self):
        if self.condition.exec(): self.block.exec()
    
    def execElse(self):
        if self.condition.exec(): self.block.exec()
        else: self.elseBlock.exec()
    
    def transpileJs(self):
        text = f"if{super().transpileJs()}"
        if hasattr(self, "elseBlock"):
            text += f" else {self.elseBlock.transpileJs()}"
        return text
    
    def transpilePy(self):
        text = f"if {super().transpilePy()}"
        if hasattr(self, "elseBlock"):
            text += "\n" + "\t" * tabID + f"else:{self.elseBlock.transpilePy()}"
        return text
    
    def transpileC(self):
        text = f"if{super().transpileC()}"
        if hasattr(self, "elseBlock"):
            text += f" else {self.elseBlock.transpileC()}"
        return text
    
    def transpileCpp(self):
        text = f"if{super().transpileCpp()}"
        if hasattr(self, "elseBlock"):
            text += f" else {self.elseBlock.transpileCpp()}"
        return text
    
    def transpileGl(self):
        text = f"when " + " ".join(super().transpileGl())
        if hasattr(self, "elseBlock"):
            text += f" else {self.elseBlock.transpileGl()}"
        return text

class WhileInstruction(ConditionalInstruction):
    def exec(self):
        while self.condition.exec(): self.block.exec()

    def transpileJs(self):
        return f"while{super().transpileJs()}"
    
    def transpilePy(self):
        return f"while {super().transpilePy()}"
    
    def transpileC(self):
        return f"while {super().transpileC()}"
    
    def transpileCpp(self):
        return f"while {super().transpileCpp()}"
    
    def transpileGl(self):
        condition, block = super().transpileGl()
        return f"when {condition} loop {block}"

class RepeatInstruction(ConditionalInstruction):
    def exec(self):
        while True:
            self.block.exec()
            if self.condition.exec(): break
    
    def transpileJs(self):
        blockText = self.block.transpileJs()[:-2] + (tabID + 1) * "\t" + f"if({self.condition.transpileJs()}) break;\n" + tabID * "\t" + "}"
        return f"while(true) {blockText}"
    
    def transpilePy(self):
        blockText = self.block.transpilePy() + "\n" + (tabID + 1) * "\t" + f"if {self.condition.transpilePy()}: break\n"
        return f"while True:{blockText}"
    
    def transpileC(self):
        blockText = self.block.transpileC()[:-2] + (tabID + 1) * "\t" + f"if({self.condition.transpileC()}) break;\n" + tabID * "\t" + "}"
        return f"while(1) {blockText}"
    
    def transpileCpp(self):
        blockText = self.block.transpileCpp()[:-2] + (tabID + 1) * "\t" + f"if({self.condition.transpileCpp()}) break;\n" + tabID * "\t" + "}"
        return f"while(true) {blockText}"
    
    def transpileGl(self):
        condition, block = super().transpileGl()
        blockText = block[:-2] + "\n" + (tabID + 1) * "\t" + f"when {condition} then exit\n" + tabID * "\t" + "}"
        return f"when TRUE loop {blockText}"

class Operation(Token):
    def argumentize(self, token):
        self.op1 = Identifier(token["op1"])
        self.op2 = Identifier(token["op2"])
        self.op  = token["operand"]
        self.exec = ({
            "+"   : self.execAdd,
            "-"   : self.execSub,
            "*"   : self.execMul,
            "/"   : self.execDiv,
            "^"   : self.execPow,
            "MOD" : self.execMod,
            "TO"  : self.execTo,
        })[self.op]
    
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

    def transpileJs(self):
        if self.op == "MOD": self.op = "%"
        op1 = self.op1.transpileJs()
        op2 = self.op2.transpileJs()
        return (op1, op2) if self.op == "TO" else f"{op1} {self.op} {op2}"
    
    def transpilePy(self):
        if self.op == "MOD": self.op = "%"
        op1 = self.op1.transpilePy()
        op2 = self.op2.transpilePy()
        return (op1, op2) if self.op == "TO" else f"{op1} {self.op} {op2}"
    
    def transpileC(self):
        if self.op == "MOD": self.op = "%"
        op1 = self.op1.transpileC()
        op2 = self.op2.transpileC()
        return (op1, op2) if self.op == "TO" else f"{op1} {self.op} {op2}"
    
    def transpileCpp(self):
        if self.op == "MOD": self.op = "%"
        op1 = self.op1.transpileCpp()
        op2 = self.op2.transpileCpp()
        return (op1, op2) if self.op == "TO" else f"{op1} {self.op} {op2}"
    
    def transpileGl(self):
        if self.op == "MOD": self.op = "%"
        op1 = self.op1.transpileGl()
        op2 = self.op2.transpileGl()
        return (op1, op2) if self.op == "TO" else f"{op1} {op2} {self.op}"

class Condition(Token):
    def argumentize(self, token):
        self.cp1 = distinguishIdOp(token["cp1"])
        self.cp2 = distinguishIdOp(token["cp2"])
        self.cp  = token["operand"]
        self.exec = ({
            "<"  : self.execLst,
            "<=" : self.execLet,
            "="  : self.execEqs,
            ">"  : self.execGrt,
            ">=" : self.execGet,
            "!=" : self.execNeq,
        })[self.cp]
    
    def execLst(self): return self.cp1.exec() <  self.cp2.exec()
    def execLet(self): return self.cp1.exec() <= self.cp2.exec()
    def execEqs(self): return self.cp1.exec() == self.cp2.exec()
    def execGrt(self): return self.cp1.exec() >  self.cp2.exec()
    def execGet(self): return self.cp1.exec() >= self.cp2.exec()
    def execNeq(self): return self.cp1.exec() != self.cp2.exec()

    def transpileJs(self):
        cp1 = self.cp1.transpileJs()
        if type(self.cp1) is Operation: cp1 = f"({cp1})"

        cp2 = self.cp2.transpileJs()
        if type(self.cp2) is Operation: cp2 = f"({cp2})"

        return f"{cp1} {self.cp} {cp2}"
    
    def transpilePy(self):
        cp1 = self.cp1.transpilePy()
        if type(self.cp1) is Operation: cp1 = f"({cp1})"

        cp2 = self.cp2.transpilePy()
        if type(self.cp2) is Operation: cp2 = f"({cp2})"

        return f"{cp1} {self.cp} {cp2}"
    
    def transpileC(self):
        cp1 = self.cp1.transpileC()
        if type(self.cp1) is Operation: cp1 = f"({cp1})"

        cp2 = self.cp2.transpileC()
        if type(self.cp2) is Operation: cp2 = f"({cp2})"

        return f"{cp1} {self.cp} {cp2}"
    
    def transpileCpp(self):
        cp1 = self.cp1.transpileCpp()
        if type(self.cp1) is Operation: cp1 = f"({cp1})"

        cp2 = self.cp2.transpileCpp()
        if type(self.cp2) is Operation: cp2 = f"({cp2})"

        return f"{cp1} {self.cp} {cp2}"
    
    def transpileGl(self):
        cp1 = self.cp1.transpileGl()
        cp2 = self.cp2.transpileGl()
        return f"{cp1} {cp2} {self.cp}"

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
    
    def transpilePy(self):
        return f"\"{self.value}\"" if self.isMsg else str(self.value)
    
    def transpileC(self):
        return f"\"{self.value}\"" if self.isMsg else f"{self.value}"
    
    def transpileCpp(self):
        return f"\"{self.value}\"" if self.isMsg else f"{self.value}"
    
    def transpileGl(self):
        return f"\"{self.value}\"" if self.isMsg else f"{self.value}"