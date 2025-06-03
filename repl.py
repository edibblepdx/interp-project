#!/usr/bin/env python3

from parse_run import parse, genAST, AmbiguousParse, ParseError
from interp import run, EvalError, EnvError, RuntimeError
from pathlib import Path
import readline

def driver():
    while True:
        try:
            s = input('> ')
            while s[-1] == '\\':
                s = s[:-1] + '\n' + input('>> ')
            if (ts := s.split())[0] == "dofile":
                try:
                    s = Path(ts[1]).read_text()
                except IndexError:
                    print("dofile expected a path")
                except FileNotFoundError as e:
                    print(f"file not found: {e}")
            t = parse(s)
            ast = genAST(t)
            run(ast) # pretty-prints and executes the AST
        except AmbiguousParse:
            print("ambiguous parse")
        except ParseError as e:
            print(f"parse error: {e}")
        except KeyboardInterrupt:
            print("ctrl-d to exit")
        except EvalError as e:
            print(f"EvalError: {e}")
        except EnvError as e:
            print(f"EnvError: {e}")
        except RuntimeError as e:
            print(f"RuntimeError: {e}")
        except EOFError:
            break

if __name__ == "__main__":
    driver()
