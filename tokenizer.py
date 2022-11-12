import re

tokenPatterns = [
    ["^ +", None],
    ["^\n+", "newline"],
    ["^<-", "arrow"],
    ["^\{\n*", "openBlock"],
    ["^\}", "closeBlock"],
    ["^,", ","],
    ["^(<|<=|>|>=|=|!=)", "comparison"],
    ["^\"[^\"\n]*\"", "message"],
    ["^-?\d+(\.\d+)?", "NUMBER"],
    ["^([\+\-\*\/\^]|MOD)", "operand"],
    ["^(WRITE|READ|IF|FOR|WHILE|REPEAT|THEN|DO|ELSE|UNTIL)", "KEYWORD"],
    ["^[a-zA-Z_]\w*", "WORD"],
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
        
        raise Exception(f"Errore : cosa cazzo hai scritto? Che cazzo significa \"{substr}\"?")

    def match(self, regexp, substr):
        _match = re.search(regexp, substr)
        if _match is None: return None
        self.cursor += len(_match.group())
        return _match.group()
