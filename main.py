import sys
from parser import Parser
from lexer import Lexer
from evaluation import Environment


def run_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    lexer = Lexer(code)
    parser = Parser(lexer)

    ast = parser.parse_program()
    env = Environment()
    env.funcs["print"] = lambda *args: print(*args)
    env.eval_program(ast)

    print(ast)




if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <filename>")
        sys.exit(1)

    run_file(sys.argv[1])
