from tokens import *
from lexer import *
from enum import IntEnum, auto
import json

class Precedence(IntEnum):
    LOWEST = 1
    EQUALS = 2      # ==, !=
    LESSGREATER = 3 # <, >, <=, >=
    SUM = 4         # +, -
    PRODUCT = 5     # *, /
    PREFIX = 6


class Parser:
    def __init__(self, l: Lexer):
        self.l: Lexer = l
        self.now_token: Token = None
        self.next_token: Token = None

        self.get_next_token()
        self.get_next_token()

    def parse_let(self):
        result = {
            "type": "let",
            "name": "",
            "value": {"expr": None}, # 표현식 파싱은 나중에
            "token": [self.now_token.value]
        }

        # 변수 이름
        self.get_next_token()
        
        if self.now_token.type != LITER:
            raise SyntaxError(f"Unexpected token {self.now_token.type}")

        if self.is_keyword():
            raise SyntaxError("Invalid variable name: keyword is not allowed.")
        
        result["name"] = self.now_token.value
        result["token"].append(self.now_token)

        # ASSIGN 확인
        self.get_next_token()
        if self.now_token.type != ASSIGN:
            raise SyntaxError("Expected '=' after variable name")
        result["token"].append(self.now_token)

        # 표현식
        self.get_next_token()
        expression = self.parse_expression()
        result["value"]["expr"] = expression

        return result

    def current_precedence(self):
        if self.now_token.type in (EQ, NEQ):
            return Precedence.EQUALS
        elif self.now_token.type in (LT, GT, LTE, GTE):
            return Precedence.LESSGREATER
        elif self.now_token.type in (PLUS, MINUS):
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
            if token.value == "true":
                self.get_next_token()
                left = {"type": "bool", "value": True}

            elif token.value == "false":
                self.get_next_token()
                left = {"type": "bool", "value": False}

            else:
                self.get_next_token()
                if self.now_token.type == LPAREN:  # call
                    left = self.parse_call(token.value)
                else:  # variable
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

    def parse_func(self):
        self.get_next_token()

        if self.now_token.type != LITER:
            raise SyntaxError("Expected function name")

        if self.is_keyword():
            raise SyntaxError("Invalid function name: keyword is not allowed.")

        func_name = self.now_token.value
        params = []
        body = []

        self.get_next_token()
        if self.now_token.type != LPAREN:
            raise SyntaxError(f"Unexpected token {self.now_token.type}")
        
        self.get_next_token() # RPAREN or LITER

        if self.now_token.type != RPAREN:
            while True:
                if self.now_token.type != LITER:
                    raise SyntaxError(f"Unexpected token {self.now_token.type}")

                if self.is_keyword():
                    raise SyntaxError("Invalid parameter name: keyword is not allowed.")

                params.append(self.now_token.value)

                self.get_next_token()

                if self.now_token.type == COMMA:
                    self.get_next_token()
                    continue
                elif self.now_token.type == RPAREN:
                    break
                else:
                    raise SyntaxError("Expected ',' or ')'")

        
        self.get_next_token() # RPAREN 소비

        # body 파싱
        if self.now_token.type != LBRACE:
            raise SyntaxError(f"Unexpected token {self.now_token.type}")

        body = self.parse_block()

        return {"type": "func", "name": func_name, "params": params, "body": body}

    def parse_return(self):
        self.get_next_token()

        # return 다음이 줄 끝 or } 이면 값 없는 return
        if self.now_token.type in (NEWLINE, RBRACE):
            return {"type": "return", "expr": None}

        expr = self.parse_expression()
        return {"type": "return", "expr": expr}
    
    def parse_if(self):
        self.get_next_token() # if 소비
        condition = self.parse_expression() # 표현식 소비

        # then body
        if self.now_token.type == LBRACE:
            then_body = self.parse_block()
        else:
            then_body = [self.parse_line()]

        else_body = None

        # else 체크
        if self.now_token.type == LITER and self.now_token.value == "else":
            self.get_next_token()

            if self.now_token.type == LBRACE:
                else_body = self.parse_block()
            else:
                else_body = [self.parse_line()]

            return {
                "type": "if",
                "condition": condition,
                "then": then_body,
                "else": else_body
            }

    def parse_for(self):
        self.get_next_token()  # for 키워드 소비

        # 조건식 파싱
        condition = self.parse_expression()

        # body 파싱
        if self.now_token.type != LBRACE:
            raise SyntaxError(f"Expected '{{' after for condition, got {self.now_token.type}")

        body = self.parse_block()

        return {
            "type": "for",
            "condition": condition,
            "body": body
        }

    def parse_block(self):
        body = []

        if self.now_token.type != LBRACE:
            raise SyntaxError(f"Expected '{{', got {self.now_token.type}")

        self.get_next_token()  # '{' 소비

        while True:
            stmt = self.parse_line()

            if stmt == "BLOCK_END":  # RBRACE 신호
                break

            if stmt is not None:
                body.append(stmt)

        self.get_next_token()  # '}' 소비
        return body




    def get_next_token(self):
        self.now_token = self.next_token
        self.next_token = self.l.return_token()

    def is_keyword(self):
        return self.now_token.type == LITER and self.now_token.value in KEYWORDS
    
    def parse_line(self):
        while self.now_token.type == NEWLINE:
            self.get_next_token()
        
        if self.now_token.type == EOF:
            return None
        
        if self.now_token.type == RBRACE:
            return "BLOCK_END"

        # LITER 토큰 처리
        if self.now_token.type == LITER:
            # 키워드 처리
            if self.now_token.value == "let":
                return self.parse_let()
            elif self.now_token.value == "func":
                return self.parse_func()
            elif self.now_token.value == "return":
                return self.parse_return()
            elif self.now_token.value == "if":
                return self.parse_if()
            elif self.now_token.value == "for":
                return self.parse_for()
            
            # let 아닌 기존 변수에 = 있을 때
            if self.next_token.type == ASSIGN:
                target_name = self.now_token.value
                self.get_next_token()  # '=' 토큰 소비
                self.get_next_token()  # '=' 다음 표현식 시작
                value_expr = self.parse_expression()
                return {
                    "type": "assign",
                    "target": target_name,
                    "value": value_expr
                }
            else:
                # 함수 호출 또는 단순 변수 표현식
                return self.parse_expression()

        else:
            # 숫자, unary 등 다른 표현식
            return self.parse_expression()


    def parse_program(self):
        nodes = []
        while True:
            node = self.parse_line()
            if node is None:
                break
            nodes.append(node)
        return nodes


if __name__ == "__main__":
    code = """
if 5 == 5 {
    print("five is five")
} else {
    print("five is not five")
} else if 55 == 5{
    print("fivefive is five")
}
    """

    lexer = Lexer(code)
    parser = Parser(lexer)

    ast = parser.parse_line()
    print(json.dumps(ast, indent=4))