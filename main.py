#The code that follows is pretty bad, viewer discretion is advised.
import sys
from interpreter import Interpreter

sys.tracebacklimit = 0

def main():
    fileLines = readFile()
    interpreter = Interpreter(fileLines, toggle_dbgMode = True)
    interpreter.build()
    if input("wish to run latest build (y|n)? ").lower() in ("y", "yes"): interpreter.run()

def readFile():
    if len(sys.argv) < 2: raise Exception("Missing filename, specify target filename to interpret.")
    fileName = f"./FILES/{sys.argv[1]}.sudo"
    
    try: return open(fileName).read()
    except Exception as e: raise Exception("Couldn't open file: invalid filename or file not found, do not include path informations or file extensions.") from None

if __name__ == "__main__":
    main()