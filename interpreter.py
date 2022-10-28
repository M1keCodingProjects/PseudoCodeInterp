# Module for handling simulation mode
class Interpreter:
    def __init__(self, fileContent, toggle_dbgMode = False):
        self.fileContent = fileContent
        self.dbgModeFlag = toggle_dbgMode
    
    def exec(self):
        self.build()
        self.run()

    def build(self):
        if self.dbgModeFlag: print("Build complete.")

    def run(self):
        if self.dbgModeFlag: print("Execution terminated successfully.")