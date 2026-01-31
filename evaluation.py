from parser import *

class Environment:
    def __init__(self, p: Parser):
        self.variables = {}
        self.funcs = {
            "print": lambda *args: print(*args)  # 임시 구현
        }

        self.p: Parser = p
    
        self.now_ast = self.p.parse_line()
    
    def eval_let(self):
        name = self.now_ast["name"]
        value_ast = self.now_ast["value"]["expr"]  # 여기서 expr만 가져옴
        self.variables[name] = self.eval_expr(value_ast)


    def eval_expr(self, ast):
        t = ast["type"]

        if t == "number":
            return int(ast["value"])
        elif t == "string":
            return ast["value"]
        elif t == "variable":
            name = ast["value"]
            if name in self.variables:
                return self.variables[name]
            else:
                raise RuntimeError(f"Undefined variable: {name}")
        elif t == "unary":
            op = ast["operator"]
            val = self.eval_expr(ast["operand"])
            if op == "+":
                return +val
            elif op == "-":
                return -val
        elif t == "binary":
            left = self.eval_expr(ast["left"])
            right = self.eval_expr(ast["right"])
            op = ast["operator"]
            if op == "+":
                return left + right
            elif op == "-":
                return left - right
            elif op == "*":
                return left * right
            elif op == "/":
                return left / right
        elif t == "call":
            func_name = ast["name"]
            args = [self.eval_expr(arg) for arg in ast["args"]]

            # print는 예약어 처리
            if func_name == "print":
                print(*args)
                return None

            if func_name in self.funcs:
                func = self.funcs[func_name]
                return func(*args)
            else:
                raise RuntimeError(f"Undefined function: {func_name}")


    def eval_line(self):
        if self.now_ast is None:
            return False

        if self.now_ast["type"] == "let":
            self.eval_let()
        elif self.now_ast["type"] == "call":
            self.eval_expr(self.now_ast)
        
        ast = self.p.parse_line()
        if ast == None:
            return False
        self.now_ast = ast
        return True