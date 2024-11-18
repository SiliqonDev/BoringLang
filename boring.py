from components.interpreter import Interpreter
from components.parser import Parser
from components.lexer import Lexer
from bits.misc import *
from values.types import Number
from values.types import BuiltInFunction

### RUN
global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number.null)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("true", Number.true)

global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("print_ret", BuiltInFunction.print_ret)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("input_int", BuiltInFunction.input_int)
global_symbol_table.set("clear", BuiltInFunction.clear)

def run(filename, text):
    lexer = Lexer(filename, text)
    tokens, error = lexer.make_tokens()
    #print(tokens)

    if error: return None, error

    ## syntax tree
    parser = Parser(tokens)
    tree = parser.parse()
    if tree.error: return None, tree.error

    # run
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(tree.node, context)

    return result.value, result.error