import os
from .base import *
from bits.error import *

class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
    
    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
    
    def subtracted_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
    
    def mul_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
    
    def mod_by(self, other):
        if isinstance(other, Number):
            return Number(self.value % other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def div_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RuntimeError(
                    other.pos_start, other.pos_end, "Division by zero", self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def floor_div_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RuntimeError(
                    other.pos_start, other.pos_end, "Division by zero", self.context
                )
            return Number(self.value // other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def to_pow_of(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def get_comparison_equals(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def get_comparison_notequals(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def get_comparison_lessthan(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def get_comparison_greaterthan(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def get_comparison_lessthanequals(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def get_comparison_greaterthanequals(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def and_with(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def or_with(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None
    
    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)
Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)

class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
    
    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
    
    def mul_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_equals(self, other):
        if isinstance(other, String):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
    
    def notted(self):
        return Number(0 if self.is_true() else 1).set_context(self.context), None

    def is_true(self):
        return len(self.value) > 0
    
    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return f'\'{self.value}\''

class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
    
    def execute(self, args):
        res = RTResult()

        if len(args) != 1:
            return res.failure(RuntimeError(
                self.pos_start, self.pos_end, 
                "Expected valid list index", self.context
            ))
        
        if isinstance(args[0], Number):
            index = args[0].value
            try:
                return res.success(self.elements[index])
            except:
                return res.failure(RuntimeError(
                    self.pos_start, self.pos_end,
                    "List index out of bounds", self.context
                ))
        else:
            return res.failure(Value.illegal_operation(self, args[0]))
    
    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None
    
    def mul_by(self, other):
        if isinstance(other, Number):
            return List(self.elements * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
        
    def notted(self):
        return Number(0 if len(self.elements) else 1).set_context(self.context), None
    
    def is_true(self):
        return len(self.elements) > 0

    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __str__(self):
        return ", ".join([str(x) for x in self.elements])

    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_return_null):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_return_null = should_return_null
    
    def execute(self, args):
        res = RTResult()
        from components.interpreter import Interpreter
        interpreter = Interpreter()
        new_context = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, new_context))
        if res.error: return res

        value = res.register(interpreter.visit(self.body_node, new_context))
        if res.error: return res
        return res.success(Number.null if self.should_return_null else value)
    
    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.should_return_null)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self):
        return f'<function {self.name}>'
    
class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)
    
    def execute(self, args):
        res = RTResult()
        context = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_method)

        res.register(self.check_and_populate_args(method.arg_names, args, context))
        if res.error: return res

        return_val = res.register(method(context))
        if res.error: return res

        return res.success(return_val)
    
    def no_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')
    
    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self):
        return f'<built-in function {self.name}>'
    
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

BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.print_ret = BuiltInFunction("print_ret")
BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.input_int = BuiltInFunction("input_int")
BuiltInFunction.clear = BuiltInFunction("clear")