from tokens import *

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Environment:
    def __init__(self, parent=None):
        self.variables = {}
        self.funcs = {}
        self.parent = parent
    
    def get_variable(self, name):
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get_variable(name)
        else:
            raise RuntimeError(f"Undefined variable: {name}")

    def get_function(self, name):
        if name in self.funcs:
            return self.funcs[name]
        elif self.parent:
            return self.parent.get_function(name)
        else:
            raise RuntimeError(f"Undefined function: {name}")



    def eval_call(self, ast):
        func_name = ast["name"]
        args = [self.eval_expr(arg) for arg in ast["args"]]

        func = self.get_function(func_name)

        if callable(func):
            return func(*args)

        local_env = Environment(parent=self)

        for param, arg in zip(func["params"], args):
            local_env.variables[param] = arg

        try:
            for stmt in func["body"]:
                local_env.eval_line(stmt)
        except ReturnException as r:
            return r.value

        return None

    def eval_let(self, node):
        name = node["name"]
        value_ast = node["value"]["expr"]
        self.variables[name] = self.eval_expr(value_ast)

    def eval_expr(self, ast):
        t = ast["type"]

        if t == "number":
            return int(ast["value"])
        elif t == "string":
            return ast["value"]
        if t == "variable":
            if ast["value"] in KEYWORDS:
                raise RuntimeError(f"Invalid variable name '{ast['value']}': reserved keyword")
            return self.get_variable(ast["value"])

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
            elif op == "==":
                return left == right
            elif op == "!=":
                return left != right
            elif op == "<":
                return left < right
            elif op == ">":
                return left > right
            elif op == "<=":
                return left <= right
            elif op == ">=":
                return left >= right
        elif t == "call":
            return self.eval_call(ast)
        elif t == "bool":
            return ast["value"]


    def eval_line(self, node):
        t = node["type"]

        if t == "let":
            self.eval_let(node)

        elif t == "call":
            self.eval_expr(node)

        elif t == "func":
            # 함수 정의는 저장만
            self.funcs[node["name"]] = node
        
        elif t == "return":
            value = None
            if node["expr"] is not None:
                value = self.eval_expr(node["expr"])
            raise ReturnException(value)
        elif t == "if":
            cond = self.eval_expr(node["condition"])
            if cond:
                for stmt in node["then"]:
                    self.eval_line(stmt)
            elif node.get("else"):
                for stmt in node["else"]:
                    self.eval_line(stmt)
        elif t == "for":
            while self.eval_expr(node["condition"]):
                for stmt in node["body"]:
                    self.eval_line(stmt)

        else:
            # 타입이 이상하거나 변수 단독일 때도 eval_expr로 검사
            self.eval_expr(node)

    
    def eval_program(self, ast_list):
        for node in ast_list:
            self.eval_line(node)