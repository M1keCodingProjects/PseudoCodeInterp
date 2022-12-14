import re

tokenPatterns = [
    ["^ +", None],
    ["^#[^\n$]*", None],
    ["^\n+", "newline"],
    ["^<-", "arrow"],
    ["^\{\n*", "openBlock"],
    ["^\}", "closeBlock"],
    ["^,", ","],
    ["^(<=|<|>=|>|=|!=)", "comparison"],
    ["^\"[^\"\n]*\"", "message"],
    ["^-?\d+(\.\d+)?", "NUMBER"],
    ["^([\+\-\*\/\^]|MOD|TO)", "operand"],
    ["^(WRITE|READ|IF|FOR|WHILE|REPEAT|THEN|DO|ELSE|UNTIL)", "KEYWORD"],
    ["^[a-zA-Z][a-zA-Z0-9]*", "WORD"],
    ["^[^ \n$]*( |\n|$)", "unknown"],
]

class Tokenizer:
    def __init__(self, fileContent):
        self.fileContent = fileContent
        self.cursor = 0
    
    def getNextToken(self):
        if self.cursor >= len(self.fileContent): return None
        substr = self.fileContent[self.cursor:]
        
        for [regexp, tokenType] in tokenPatterns:
            tokenValue = self.match(regexp, substr)
            if tokenValue is None: continue
            if tokenType is None: return self.getNextToken()
            
            if tokenType == "message": tokenValue = tokenValue[1:-1]
            
            return {
                "type": tokenType,
                "value": tokenValue
            }
        
        raise Exception(f"The tokenizer found unmatchable text: \"{substr}\", this is a bug and should be reported.")

    def match(self, regexp, substr):
        _match = re.search(regexp, substr)
        if _match is None: return None
        self.cursor += len(_match.group())
        return _match.group()
