#The code that follows is pretty bad, viewer discretion is advised.
import sys
from interpreter import Interpreter

def main():
    fileLines : list = readFile()
    interpreter = Interpreter(fileLines, toggle_dbgMode = True)
    interpreter.exec()

def readFile():
    try: fileName : str = f"./FILES/{sys.argv[1]}.sudo"
    except: print("Error: Specify target filename to interpret.")
    
    try:
        with open(fileName) as fd: return fd.read()
    except: print("Error: Couldn't open file: invalid filename or file not found, do not include path informations or file extensions.")

if __name__ == "__main__":
    main()