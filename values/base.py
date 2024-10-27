from bits.results import RTResult
from bits.misc import *
from bits.error import *

### VALUE

class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()
    
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def set_context(self, context=None):
        self.context = context
        return self
    
    def added_to(self, other):
        return None, self.illegal_operation(other)
    def subtracted_by(self, other):
        return None, self.illegal_operation(other)
    def mul_by(self, other):
        return None, self.illegal_operation(other)
    def mod_by(self, other):
        return None, self.illegal_operation(other)
    def div_by(self, other):
        return None, self.illegal_operation(other)
    def floor_div_by(self, other):
        return None, self.illegal_operation(other)
    def to_pow_of(self, other):
        return None, self.illegal_operation(other)
    def get_comparison_equals(self, other):
        return None, self.illegal_operation(other)
    def get_comparison_notequals(self, other):
        return None, self.illegal_operation(other)
    def get_comparison_lessthan(self, other):
        return None, self.illegal_operation(other)
    def get_comparison_greaterthan(self, other):
        return None, self.illegal_operation(other)
    def get_comparison_lessthanequals(self, other):
        return None, self.illegal_operation(other)
    def get_comparison_greaterthanequals(self, other):
        return None, self.illegal_operation(other)
    def and_with(self, other):
        return None, self.illegal_operation(other)
    def or_with(self, other):
        return None, self.illegal_operation(other)
    def notted(self):
        return None, self.illegal_operation()
    def execute(self, args):
        return RTResult().failure(self.illegal_operation())
    def copy(self):
        raise Exception("No copy method defined")
    def is_true(self):
        return False
    def illegal_operation(self, other=None):
        if not other: other = self
        return RuntimeError(
            self.pos_start, other.pos_end,
            'Illegal Operation', self.context
        )

### BASE FUNCTION

class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"
    
    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context
    
    def check_args(self, arg_names, args):
        res = RTResult()

        if len(args) != len(arg_names):
            return res.failure(RuntimeError(
                self.pos_start, self.pos_end,
                f"expected {len(arg_names)} arguments, but {len(args)} were passed.",
                self.context
            ))
        
        return res.success(None)
    
    def populate_args(self, arg_names, args, context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(context)
            context.symbol_table.set(arg_name, arg_value)
    
    def check_and_populate_args(self, arg_names, args, context):
        res = RTResult()

        res.register(self.check_args(arg_names, args))
        if res.error: return res
        self.populate_args(arg_names, args, context)
        return res.success(None)
