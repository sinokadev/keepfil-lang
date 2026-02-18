from tokens import *

def is_liter(ch):
    if ch:
        return ("a" <= ch <= "z") or ("A" <= ch <= "Z") or (ch == "_")
    else:
        return False

def is_number(ch):
    if ch:
        return ch in "0123456789"
    else:
        return False

class Lexer:
    def __init__(self, code):
        self.pos = 0
        self.next_pos = 0
        self.reading = ""
        self.code = code

        self.read_text() # 초기 좌표 셋팅하기

    def read_text(self):
        if self.next_pos >= len(self.code):
            self.reading = None
        else:
            self.reading = self.code[self.next_pos]
        self.pos = self.next_pos
        self.next_pos += 1

    def str_lexing(self):
        self.read_text()
        string = ""
        while self.reading and self.reading != "\"":
            string += self.reading
            self.read_text()
        self.read_text()
        return Token(STR, string)

    def liter_lexing(self):
        liter = ""
        while is_liter(self.reading):
            liter += self.reading
            self.read_text()

        return Token(LITER, liter)

    def number_lexing(self):
        number = ""
        while is_number(self.reading):
            
            number += self.reading
            self.read_text()

        return Token(NUMBER, number)
    
    def peek_char(self):
        if self.next_pos >= len(self.code):
            return None
        return self.code[self.next_pos]


    def return_token(self):
        tok = None

        while self.reading and self.reading.isspace() and self.reading != "\n":
            self.read_text()

        if self.reading == "#":
            while self.reading and self.reading != "\n":
                self.read_text()
            # 다음 토큰 처리
            return self.return_token()

        match self.reading:
            case "(":
                tok = Token(LPAREN, self.reading)
            case ")":
                tok = Token(RPAREN, self.reading)
            case "{":
                tok = Token(LBRACE, self.reading)
            case "}":
                tok = Token(RBRACE, self.reading)
            case "=":
                if self.peek_char() == "=":
                    ch = self.reading
                    self.read_text()
                    tok = Token(EQ, ch + self.reading)
                else:
                    tok = Token(ASSIGN, self.reading)
            case "!":
                if self.peek_char() == "=":
                    ch = self.reading
                    self.read_text()
                    tok = Token(NEQ, ch + self.reading)
                else:
                    tok = Token(IDK, self.reading)
            case "<":
                if self.peek_char() == "=":
                    ch = self.reading
                    self.read_text()
                    tok = Token(LTE, ch + self.reading)
                else:
                    tok = Token(LT, self.reading)

            case ">":
                if self.peek_char() == "=":
                    ch = self.reading
                    self.read_text()
                    tok = Token(GTE, ch + self.reading)
                else:
                    tok = Token(GT, self.reading)
            case "+":
                tok = Token(PLUS, self.reading)
            case "*":
                tok = Token(STAR, self.reading)
            case "-":
                tok = Token(MINUS, self.reading)
            case "/":
                tok = Token(SLASH, self.reading)
            case ",":
                tok = Token(COMMA, self.reading)
                
            case None:
                return Token(EOF, self.reading)
            case "\n":
                tok = Token(NEWLINE, self.reading)
            case "\"":
                tok = self.str_lexing()
            case _:
                if is_liter(self.reading):
                    return self.liter_lexing()
                if is_number(self.reading):
                    return self.number_lexing()
                else:
                    tok = Token(IDK, self.reading)


        self.read_text()
        return tok


if __name__ == "__main__":
    code = """
let asdf = 5
let b = "tesT"

asdf == 5

"""
    lexer = Lexer(code)
    tokens = []

    while True:
        tok = lexer.return_token()
        tokens.append(tok)
        if tok.type == EOF:
            break

    print(tokens)