from components.interpreter import Interpreter
from components.parser import Parser
from components.lexer import Lexer
from bits.misc import *
from values.types import *

### CIRCULAR IMPORT TEMP SOLUTION
class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)
    
    def execute(self, args):
        res = RTResult()
        context = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_method)

        res.register(self.check_and_populate_args(method.arg_names, args, context))
        if res.should_return(): return res

        return_val = res.register(method(context))
        if res.should_return(): return res

        return res.success(return_val)
    
    def no_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')
    
    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self):
        return f'<built-in-function {self.name}>'
    
    def execute_print(self, context):
        print(str(context.symbol_table.get('value')))
        return RTResult().success(Number.null)
    execute_print.arg_names = ['value']

    def execute_print_ret(self, context):
        return RTResult().success(String(str(context.symbol_table.get('value'))))
    execute_print_ret.arg_names = ['value']

    def execute_input(self, context):
        text = input()
        return RTResult().success(String(text))
    execute_input.arg_names = []

    def execute_input_int(self, context):
        text = input()
        try:
            n = int(text)
        except ValueError:
            return RTResult().failure(RuntimeError(
                self.pos_start.copy(), self.pos_end.copy(),
                "Given input could not be converted to number.", context
            ))
        return RTResult().success(Number(n))
    execute_input_int.arg_names = []
    
    def execute_clear(self, context):
        os.system('cls' if os.name == "nt" else 'clear')
        return RTResult().success(Number.null)
    execute_clear.arg_names = []

    def execute_len(self, context):
        itr = context.symbol_table.get('iterable')

        if not (isinstance(itr, List) or isinstance(itr, String)):
            return RTResult().failure(RuntimeError(
                self.pos_start, self.pos_end,
                "Argument must be an iterable", context
            ))
    
        return RTResult().success(Number(len(itr.elements)) if isinstance(itr, List) else Number(len(itr.value)))
    execute_len.arg_names = ['iterable']

    def execute_run(self, context):
        fn = context.symbol_table.get("fn")

        if not isinstance(fn, String):
            return RTResult().failure(
                RuntimeError(
                    self.pos_start, self.pos_end,
                    "Argument must be string", context
                )
            )
        
        fn = fn.value

        try:
            with open(fn, 'r') as f:
                script = f.read()
        except Exception as e:
            return RTResult().failure(
                RuntimeError(
                    self.pos_start, self.pos_end,
                    f"Failed to load script \"{fn}\"\n"+str(e), context
                )
            )
        
        _, error = run(fn, script)

        if error:
            return RTResult().failure(
                RuntimeError(
                    self.pos_start, self.pos_end,
                    f"Failed to finish executing script \"{fn}\"\n"+error.as_string(), context
                )
            )
        
        return RTResult().success(Number.null)
    execute_run.arg_names = ["fn"]

BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.print_ret = BuiltInFunction("print_ret")
BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.input_int = BuiltInFunction("input_int")
BuiltInFunction.clear = BuiltInFunction("clear")
BuiltInFunction.len = BuiltInFunction("len")
BuiltInFunction.run = BuiltInFunction("run")

####

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number.null)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("true", Number.true)

global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("print_ret", BuiltInFunction.print_ret)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("input_int", BuiltInFunction.input_int)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("len", BuiltInFunction.len)
global_symbol_table.set("run", BuiltInFunction.run)

### RUN
def run(filename, text):
    lexer = Lexer(filename, text)
    tokens, error = lexer.make_tokens()
    print(tokens)

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