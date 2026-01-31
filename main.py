import sys
from parser import Parser
from lexer import Lexer
from evaluation import Environment

def run_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    lexer = Lexer(code)
    parser = Parser(lexer)
    env = Environment(parser)

    while env.eval_line():
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 run.py <filename>")
        sys.exit(1)

    run_file(sys.argv[1])
