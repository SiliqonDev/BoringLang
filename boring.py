import string
### CONSTANTS

DIGITS = "0123456789"
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS + "_"

### ERRORS

class Error:
    def __init__(self, pos_start, pos_end, error_name, info):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.info = info
    
    def as_string(self):
        result = f"{self.error_name}: {self.info}"
        result += f"\nFile {self.pos_start.filename}: line {self.pos_start.ln + 1}, col {self.pos_start.col}"
        return result
    
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, info):
        super().__init__(pos_start, pos_end, "Illegal Character", info)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, info):
        super().__init__(pos_start, pos_end, "Invalid Syntax", info)

class RuntimeError(Error):
    def __init__(self, pos_start, pos_end, info, context):
        super().__init__(pos_start, pos_end, "Runtime Error", info)
        self.context = context
    
    def as_string(self):
        result = self.generate_traceback()
        result += f"{self.error_name}: {self.info}"
        return result
    
    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        context = self.context

        while context:
            result = f'    File {pos.filename}, line {pos.ln + 1}, in {context.display_name}\n' + result
            pos = context.parent_entry_pos
            context = context.parent
        
        return "Traceback (most recent call last):\n" + result

### TOKENS

T_INT = "INT"
T_FLOAT = "FLOAT"
T_IDENTIFIER = "IDENTIFIER"
T_KEYWORD = "KEYWORD"
T_EQUALS = "EQUALS"
T_PLUS = "PLUS"
T_MINUS = "MINUS"
T_MUL = "MUL"
T_DIV = "DIV"
T_FLOORDIV = "FLOORDIV"
T_POW = "POW"
T_LPAREN = "LPAREN"
T_RPAREN = "RPAREN"
T_EOF = "EOF"

KEYWORDS = [
    "var"
]

TokenReference = {
    "+" : T_PLUS,
    "-" : T_MINUS,
    "*" : T_MUL,
    "^": T_POW,
    "/" : T_DIV,
    #"//": T_FLOORDIV,
    "(" : T_LPAREN,
    ")" : T_RPAREN,
    "=" : T_EQUALS
}

### POSITION

class Position:
    def __init__(self, index, ln, col, filename, filetext):
        self.index = index
        self.ln = ln
        self.col = col
        self.filename = filename
        self.filetext = filetext
    
    def next(self, current_char=None):
        self.index += 1
        self.col += 1

        if current_char == "\n":
            self.ln += 1
            self.col = 0
        
        return self
    
    def copy(self):
        return Position(self.index, self.ln, self.col, self.filename, self.filetext)

class Token:
    def __init__(self, type, value=None, pos_start=None, pos_end=None):
        self.type = type
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = self.pos_start.copy()
            self.pos_end.next()

        if pos_end:
            self.pos_end = pos_end.copy()

    def matches(self, type, value):
        return self.type == type and self.value == value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
### LEXER

class Lexer:
    def __init__(self, filename, text):
        self.filename = filename
        self.text = text
        self.pos = Position(-1, 0, -1, filename, text)
        self.current_char = None
        self.next()
    
    def next(self):
        self.pos.next(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None
    
    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            # space or tab
            if self.current_char in ' \t':
                self.next()
                continue

            # numbers
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            
            # letter
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())

            # operators
            elif self.current_char in TokenReference.keys():
                tokens.append(Token(TokenReference[self.current_char], pos_start=self.pos))
                self.next()
            
            # error
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.next()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(T_EOF, pos_start=self.pos))
        return tokens, None
    
    def make_number(self):
        num_str = ""
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if dot_count == 1: break
            if self.current_char == '.':
                dot_count += 1
                num_str += "."
            else:
                num_str += self.current_char
            self.next()

        if dot_count == 0:
            return Token(T_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(T_FLOAT, float(num_str), pos_start, self.pos)
    
    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS:
            id_str += self.current_char
            self.next()
        
        tok_type = T_KEYWORD if id_str in KEYWORDS else T_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

### NODES

class NumberNode:
    def __init__(self, token):
        self.tok = token
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
    
    def __repr__(self):
        return f'{self.tok}'

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = var_name_tok.pos_start
        self.pos_end = var_name_tok.pos_end

class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        
        self.pos_start = var_name_tok.pos_start
        self.pos_end = var_name_tok.pos_end
    
class BinOpNode:
    def __init__(self, left, op_tok, right):
        self.left = left
        self.op_tok = op_tok
        self.right = right

        self.pos_start = self.left.pos_start
        self.pos_end = self.right.pos_end
    
    def __repr__(self):
        return f'({self.left}, {self.op_tok}, {self.right})'

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = self.node.pos_end
    
    def __repr__(self):
        return f"({self.op_tok}, {self.node})"

### PARSE RESULT

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
    
    def register_next(self):
        self.advance_count += 1

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node
    
    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
            return self

### PARSER

class Parser:
    def __init__(self, tokens):
        self.toks = tokens
        self.tok_index = -1
        self.next()
    
    def next(self):
        self.tok_index += 1
        if self.tok_index < len(self.toks):
            self.current_tok = self.toks[self.tok_index]
        return self.current_tok
    
    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != T_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected valid operator"
            ))
        return res
    
    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (T_INT, T_FLOAT):
            res.register_next()
            self.next()
            return res.success(NumberNode(tok))
        
        if tok.type == T_IDENTIFIER:
            res.register_next()
            self.next()
            return res.success(VarAccessNode(tok))
        
        elif tok.type == T_LPAREN:
            res.register_next()
            self.next()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == T_RPAREN:
                res.register_next()
                self.next()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"
                ))
        
        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end, "Expected int, float, identifier, '+', '-' or '('"
        ))
    
    def power(self):
        return self.bin_op(self.atom, (T_POW, ), func_b=self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type == T_MINUS:
            res.register_next()
            self.next()
            factor =  res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (T_POW, T_MUL, T_FLOORDIV, T_DIV))

    def expr(self):
        res = ParseResult()
        if self.current_tok.matches(T_KEYWORD, "var"):
            res.register_next()
            self.next()

            if self.current_tok.type != T_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected Identifier"
                ))
            
            var_name = self.current_tok
            res.register_next()
            self.next()

            if self.current_tok.type != T_EQUALS:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))
            
            res.register_next()
            self.next()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expr))

        node = res.register(self.bin_op(self.term, (T_PLUS, T_MINUS)))

        if res.error:
            return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'var', int, float, identifier, '+', '-' or '('"
            ))
        return res.success(node)
    
    ###

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())

        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register_next()
            self.next()
            right = res.register(func_b())

            if res.error: return res

            left = BinOpNode(left, op_tok, right)
        
        return res.success(left)

### RUNTIME RESULT

class RTResult():
    def __init__(self):
        self.value = None
        self.error = None
    
    def register(self, res):
        if res.error: self.error = res.error
        return res.value
    
    def success(self, value):
        self.value = value
        return self
    
    def failure(self, error):
        self.error = error
        return self

### VALUES

class Number:
    def __init__(self, value):
        self.value = value
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
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
    
    def subtracted_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
    
    def mul_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
    
    def div_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RuntimeError(
                    other.pos_start, other.pos_end, "Division by zero", self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
    
    def floor_div_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RuntimeError(
                    other.pos_start, other.pos_end, "Division by zero", self.context
                )
            return Number(self.value // other.value).set_context(self.context), None
        
    def to_pow_of(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
    
    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self):
        return str(self.value)

### CONTEXT

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

### SYMBOL TABLE

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None
    
    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value
    
    def set(self, name, value):
        self.symbols[name] = value
    
    def remove(self,name):
        del self.symbols[name]

### INTERPRETER

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)
    
    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    ####

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
            )
    
    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if value is None:
            return res.failure(RuntimeError(
                node.pos_start, node.pos_end, f"'{var_name}' is not defined", context
            ))
        
        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)
    
    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left, context))
        if res.error: return res
        right = res.register(self.visit(node.right, context))
        if res.error: return res

        error = None
        if node.op_tok.type == T_PLUS:
            result, error = left.added_to(right)
        if node.op_tok.type == T_MINUS:
            result, error = left.subtracted_by(right)
        if node.op_tok.type == T_MUL:
            result, error = left.mul_by(right)
        if node.op_tok.type == T_DIV:
            result, error = left.div_by(right)
        if node.op_tok.type == T_FLOORDIV:
            result, error = left.floor_div_by(right)
        if node.op_tok.type == T_POW:
            result, error = left.to_pow_of(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))
    
    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None
        if node.op_tok.type == T_MINUS:
            number, error = number.mul_by(Number(-1))

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))
    
### RUN

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))
def run(filename, text):
    lexer = Lexer(filename, text)
    tokens, error = lexer.make_tokens()

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