from tokens import *
from lexer import *
from enum import IntEnum, auto

class Precedence(IntEnum):
    LOWEST = 1
    SUM = 2       # +, -
    PRODUCT = 3   # *, /
    PREFIX = 4    # -x, !x


class Expression:
    def __init__(self):
        pass


class Parser:
    def __init__(self, l: Lexer):
        self.l: Lexer = l
        self.now_token: Token = None
        self.next_token: Token = None

        self.get_next_token()
        self.get_next_token()

    def let_parse(self):
        result = {
            "type": "let",
            "name": "",
            "datatype": "",
            "value": {"expr": None}, # 표현식 파싱은 나중에
            "token": [self.now_token.value]
        }

        # 타입
        self.get_next_token()
        result["datatype"] = self.now_token.value
        result["token"].append(self.now_token)

        # 변수 이름
        self.get_next_token()
        result["name"] = self.now_token.value
        result["token"].append(self.now_token)

        # ASSIGN 확인
        self.get_next_token()
        if self.now_token.type != ASSIGN:
            raise SyntaxError("Expected '=' after variable name")
        result["token"].append(self.now_token)

        # 표현식 (현재는 placeholder)
        self.get_next_token()
        expression = self.parse_expression()
        result["value"]["expr"] = expression

        return result

    def current_precedence(self):
        if self.now_token.type in (PLUS, MINUS):
            return Precedence.SUM
        elif self.now_token.type in (STAR, SLASH):
            return Precedence.PRODUCT
        else:
            return Precedence.LOWEST

    def parse_call(self, function_name):
        self.get_next_token()
        args = []

        while self.now_token.type not in (RPAREN, EOF, NEWLINE):
            arg = self.parse_expression()
            args.append(arg)

            if self.now_token.type == COMMA:
                self.get_next_token()


        self.get_next_token()
        return {"type": "call", "name": function_name, "args": args}


    def parse_expression(self, precedence=Precedence.LOWEST):
        token = self.now_token
        if token.type == NUMBER:
            self.get_next_token()
            left = {"type": "number", "value": token.value}
        elif token.type == LITER:
            self.get_next_token()
            if self.now_token.type == LPAREN: # call
                left = self.parse_call(token.value)
            else: # var
                left = {"type": "variable", "value": token.value}
        elif token.type == STR:
            self.get_next_token()
            left = {"type": "string", "value": token.value}


        elif token.type in (PLUS, MINUS):  # unary prefix
            self.get_next_token()
            operand = self.parse_expression(Precedence.PREFIX)
            left = {"type": "unary", "operator": token.value, "operand": operand}
        else:
            raise SyntaxError(f"Unexpected token {token.type}")
        
        while precedence < self.current_precedence():
            token = self.now_token
            self.get_next_token()
            right = self.parse_expression(self.current_precedence())
            left = {"type": "binary", "operator": token.value, "left": left, "right": right}

        return left


    def get_next_token(self):
        self.now_token = self.next_token
        self.next_token = self.l.return_token()

    def parse_line(self):
        result = None

        while self.now_token.type == NEWLINE:
            self.get_next_token()
        
        if self.now_token.type == EOF:
            return None

        if self.now_token.type == LITER:
            if self.now_token.value == "let":
                result = self.let_parse()
            else:
                # 변수 또는 함수 호출 같은 일반 표현식
                result = self.parse_expression()
        else:
            # 숫자, unary 등 다른 표현식
            result = self.parse_expression()

        return result

if __name__ == "__main__":
    code = """
    let int myvar = 52
    print(\"My Way\")
    print(myvar + 52)
    """

    lexer = Lexer(code)
    parser = Parser(lexer)

    print(parser.parse_line())
    print(parser.parse_line())
    print(parser.parse_line())