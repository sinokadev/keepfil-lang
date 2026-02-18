LPAREN = "LPAREN"
RPAREN = "RPAREN"
QUOT = "QUOT"
LITER = "LITER"
STR = "STR"
IDK = "IDK"
EOF = "EOF"
ASSIGN = "ASSIGN"
PLUS = "PLUS"
MINUS = "MINUS"
STAR = "STAR"
SLASH = "SLASH"
NUMBER = "NUMBER"
NEWLINE = "NEWLINE"
COMMA = "COMMA"
LBRACE = "LBRACE"
RBRACE = "RBRACE"

EQ = "EQ"        # ==
NEQ = "NEQ"      # !=
LT = "LT"        # <
GT = "GT"        # >
LTE = "LTE"      # <=
GTE = "GTE"      # >=

KEYWORDS = {"let", "func", "return", "from", "in", "false", "true", "if", "else"}
TYPES = {"int", "str", "bool"}

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
        
    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"
