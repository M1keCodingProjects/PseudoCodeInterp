# Module for handling simulation mode
from parser import Parser
class Interpreter:
    def __init__(self, fileContent, toggle_dbgMode = False):
        self.dbgModeFlag = toggle_dbgMode
        self.parser   = Parser(fileContent)
    
    def exec(self):
        self.build()
        self.run()

    def parse(self):
        self.parser.parse()

    def build(self):
        self.parse()
        if self.dbgModeFlag: print("Build complete.")

    def run(self):
        if self.dbgModeFlag: print("Execution terminated successfully.")