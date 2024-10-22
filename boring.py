import string
from string_with_arrows import *

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
        result += '\n\n' + string_with_arrows(self.pos_start.filetext, self.pos_start, self.pos_end)
        return result
    
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, info):
        super().__init__(pos_start, pos_end, "Illegal Character", info)

class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, info):
        super().__init__(pos_start, pos_end, "Expected Character", info)

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
        result += '\n\n' + string_with_arrows(self.pos_start.filetext, self.pos_start, self.pos_end)
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
T_STRING = "STRING"
T_IDENTIFIER = "IDENTIFIER"
T_KEYWORD = "KEYWORD"
T_EQUALS = "EQUALS"
T_EE = "VALUE_EQUALS"
T_NE = "NOT_EQUALS"
T_LE = "LESS_THAN"
T_GE = "GREATER_THAN"
T_LTE = "LESS_THAN_EQUALS"
T_GTE = "GREATER_THAN_EQUALS"
T_PLUS = "PLUS"
T_MINUS = "MINUS"
T_MUL = "MUL"
T_MOD = "MOD"
T_DIV = "DIV"
T_FLOORDIV = "FLOORDIV"
T_POW = "POW"
T_LPAREN = "LPAREN"
T_RPAREN = "RPAREN"
T_LSQUARE = "LSQUARE"
T_RSQUARE = "RSQUARE"
T_COMMA = "COMMA"
T_ARROW = "ARROW"
T_EOF = "EOF"

KEYWORDS = [
    "var",
    'and',
    'or',
    'not',
    'if',
    'then',
    'elif',
    'else',
    'for',
    'to',
    'do',
    'step',
    'while',
    'fn'
]

TokenReference = {
    "+" : T_PLUS,
    "-" : T_MINUS,
    "*" : T_MUL,
    "%" : T_MOD,
    "/" : T_DIV,
    "(" : T_LPAREN,
    ")" : T_RPAREN,
    "[" : T_LSQUARE,
    "]" : T_RSQUARE,
    "=" : T_EQUALS,
    "," : T_COMMA
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
    
    def previous(self, current_char=None):
        self.index -= 1
        self.col -= 1

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
    
    def previous(self):
        self.pos.previous(self.current_char)
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
            
            elif self.current_char == '"':
                tokens.append(self.make_string())

            # multi-char operators
            elif self.current_char == "!":
                tok, error = self.make_multichar_operator(
                    "!", "=",
                    T_NE, None
                )
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == "/":
                tok, error = self.make_multichar_operator(
                    "/", "/",
                    T_FLOORDIV, T_DIV
                )
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == "*":
                tok, error = self.make_multichar_operator(
                    "*", "*",
                    T_POW, T_MUL
                )
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == "=":
                tok, error = self.make_multichar_operator(
                    "=", "=",
                    T_EE, T_EQUALS
                )
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == "<":
                tok, error = self.make_multichar_operator(
                    "<", "=",
                    T_LTE, T_LE
                )
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == ">":
                tok, error = self.make_multichar_operator(
                    ">", "=",
                    T_GTE, T_GE
                )
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == '-':
                tok, error = self.make_multichar_operator(
                    "-", ">",
                    T_ARROW, T_MINUS
                )
                if error: return [], error
                tokens.append(tok)

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
    
    def make_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_char = False
        self.next()

        escape_chars = {
            'n' : '\n',
            't' : '\t'
        }

        while self.current_char != None and (self.current_char != '"' or escape_char):
            if escape_char:
                string += escape_chars.get(self.current_char, self.current_char)
                escape_char = False
            else:
                if self.current_char == '\\':
                    escape_char = True
                else:
                    string += self.current_char
            self.next()
        
        self.next()
        return Token(T_STRING, string, pos_start, self.pos)
    
    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS:
            id_str += self.current_char
            self.next()
        
        tok_type = T_KEYWORD if id_str in KEYWORDS else T_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)
    
    def make_multichar_operator(self, firstchar, nextchar, success, fail):
        pos_start = self.pos.copy()
        self.next()

        if self.current_char == nextchar:
            self.next()
            return Token(success, pos_start=pos_start, pos_end=self.pos), None
        
        self.next()
        if fail is None:
            return None, ExpectedCharError(
                pos_start, self.pos,
                f"'{nextchar}' (after '{firstchar}')"
            )
        
        self.previous()
        return Token(fail, pos_start=pos_start, pos_end=self.pos), None

### NODES

class NumberNode:
    def __init__(self, token):
        self.tok = token
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
    
    def __repr__(self):
        return f'{self.tok}'

class StringNode:
    def __init__(self, token):
        self.tok = token
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
    
    def __repr__(self):
        return f'{self.tok}'

class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end

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

class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case
        
        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[-1][0]).pos_end

class ForNode:
    def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

class WhileNode:
    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_start

class FuncDefNode:
    def __init__(self, var_name_tok, arg_name_toks, body_node):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node

        if self.var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start
        
        self.pos_end = self.body_node.pos_end

class CallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[-1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end

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
        
    def __repr__(self):
        return f"{self.node}, {self.error}"

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
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '+', '-', '*', '/', '//', '^', '==', '!=', '<', '>', <=', '>=', 'and' or 'or'"
            ))
        return res
    
    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if not self.current_tok.type == T_LSQUARE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '['"
            ))
        
        res.register_next()
        self.next()

        if self.current_tok.type == T_RSQUARE:
            res.register_next()
            self.next()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected ']', 'var', 'if', 'for', 'while', 'fn', int, float, identifier, '+', '-'. '[' or '('"
                ))
            
            while self.current_tok.type == T_COMMA:
                res.register_next()
                self.next()

                element_nodes.append(res.register(self.expr()))
                if res.error: return res
            
            if self.current_tok.type != T_RSQUARE:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ',' or ']'"
                ))
            
            res.register_next()
            self.next()
        
        return res.success(ListNode(
            element_nodes, pos_start, self.current_tok.pos_end.copy()
        ))

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(T_KEYWORD, "if"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'if'"
            ))
        
        res.register_next()
        self.next()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(T_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '1'"
            ))
        
        res.register_next()
        self.next()

        expr = res.register(self.expr())
        if res.error: return res
        cases.append((condition, expr))

        while self.current_tok.matches(T_KEYWORD, 'elif'):
            res.register_next()
            self.next()

            condition = res.register(self.expr())
            if res.error: return res

            if not self.current_tok.matches(T_KEYWORD, 'then'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected 'then'"
                ))
            
            res.register_next()
            self.next()

            expr = res.register(self.expr())
            if res.error: return res
            cases.append((condition, expr))
        
        if self.current_tok.matches(T_KEYWORD, 'else'):
            res.register_next()
            self.next()

            else_case = res.register(self.expr())
            if res.error: return res
        
        return res.success(IfNode(cases, else_case))
    
    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(T_KEYWORD, 'for'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'for'"
            ))
        
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

        start_value = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(T_KEYWORD, "to"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'to'"
            ))
        
        res.register_next()
        self.next() 

        end_value = res.register(self.expr())
        if res.error: return res

        if self.current_tok.matches(T_KEYWORD, 'step'):
            res.register_next()
            self.next()

            step_value = res.register(self.expr())
            if res.error: return res
        else:
            step_value = None
        
        if not self.current_tok.matches(T_KEYWORD, 'do'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'do'"
            ))
        
        res.register_next()
        self.next()

        body = res.register(self.expr())
        if res.error: return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body))
    
    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(T_KEYWORD, 'while'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'while'"
            ))
        
        res.register_next()
        self.next()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(T_KEYWORD, 'do'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'do'"
            ))
        
        res.register_next()
        self.next()

        body = res.register(self.expr())
        if res.error: return res

        return res.success(WhileNode(condition, body))

    def power(self):
        return self.bin_op(self.call, (T_POW, ), func_b=self.factor)
    
    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_tok.type == T_LPAREN:
            res.register_next()
            self.next()
            arg_nodes = []
            
            if self.current_tok.type == T_RPAREN:
                res.register_next()
                self.next()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')', 'var', 'if', 'for', 'while', 'fn', 'not', int, float, identifier, '+', '-' '[', or '('"
                    ))
                
                while self.current_tok.type == T_COMMA:
                    res.register_next()
                    self.next()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res
                
                if self.current_tok.type != T_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ',' or ')'"
                    ))
                
                res.register_next()
                self.next()

            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (T_INT, T_FLOAT):
            res.register_next()
            self.next()
            return res.success(NumberNode(tok))
        
        elif tok.type == T_STRING:
            res.register_next()
            self.next()
            return res.success(StringNode(tok))
    
        elif tok.type == T_IDENTIFIER:
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
            
        elif tok.type == T_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error: return res
            return res.success(list_expr)

        elif tok.matches(T_KEYWORD, "if"):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)
        
        elif tok.matches(T_KEYWORD, "for"):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)
        
        elif tok.matches(T_KEYWORD, 'while'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)

        elif tok.matches(T_KEYWORD, 'fn'):
            fn_expr = res.register(self.func_def())
            if res.error: return res
            return res.success(fn_expr)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end, "Expected int, float, identifier, '+', '-', '(', '[', 'if', 'for', 'while' or 'fn'"
        ))

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
        return self.bin_op(self.factor, (T_POW, T_MOD, T_MUL, T_FLOORDIV, T_DIV))
    
    def arith_expr(self):
        return self.bin_op(self.term, (T_PLUS, T_MINUS))
    
    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(T_KEYWORD, "not"):
            op_tok = self.current_tok
            res.register_next()
            self.next()

            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))
        
        node = res.register(self.bin_op(self.arith_expr, (T_EE, T_NE, T_LE, T_GE, T_LTE, T_GTE)))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end, "Expected int, float, identifier, '+', '-' or '(', '[', 'not'"
            ))
        
        return res.success(node)

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

        node = res.register(self.bin_op(self.comp_expr, ((T_KEYWORD, "and"), (T_KEYWORD, "or"))))

        if res.error:
            return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end, "Expected 'var', 'if', 'for', 'while', 'fn', 'not', int, float, identifier, '+', '-', '[' or '('"
            ))
        return res.success(node)
    
    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(T_KEYWORD, "fn"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'fn'"
            ))
        
        res.register_next()
        self.next()

        if self.current_tok.type == T_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_next()
            self.next()

            if self.current_tok.type != T_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '('"
                ))
        else:
            var_name_tok = None
            if self.current_tok.type != T_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier or '('"
                ))
        
        res.register_next()
        self.next()

        arg_name_toks = []
        if self.current_tok.type == T_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_next()
            self.next()

            while self.current_tok.type == T_COMMA:
                res.register_next()
                self.next() 

                if self.current_tok.type != T_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected identifier"
                    ))
                
                arg_name_toks.append(self.current_tok)
                res.register_next()
                self.next()
            
            if self.current_tok.type != T_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ',' or ')"
                ))
        else:
            if self.current_tok.type != T_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier or ')"
                ))
            
        res.register_next()
        self.next()

        if self.current_tok.type != T_ARROW:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '->'"
            ))
        
        res.register_next()
        self.next()

        node_to_return = res.register(self.expr())
        if res.error: return res

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, node_to_return))

    ###

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
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

class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
    
    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        new_context = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, new_context))
        if res.error: return res

        value = res.register(interpreter.visit(self.body_node, new_context))
        if res.error: return res
        return res.success(value)
    
    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
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
        return f'<built-in-function {self.name}>'

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
    
    def notted(self):
        return Number(0 if self.is_true() else 1).set_context(self.context), None

    def is_true(self):
        return len(self.value) > 0
    
    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self):
        return f'{self.value}'

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
        copy = List(self.elements[:])
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'

### CONTEXT

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

### SYMBOL TABLE

class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent
    
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
    
    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.error: return res
        
        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
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
        elif node.op_tok.type == T_MINUS:
            result, error = left.subtracted_by(right)
        elif node.op_tok.type == T_MUL:
            result, error = left.mul_by(right)
        elif node.op_tok.type == T_MOD:
            result, error = left.mod_by(right)
        elif node.op_tok.type == T_DIV:
            result, error = left.div_by(right)
        elif node.op_tok.type == T_FLOORDIV:
            result, error = left.floor_div_by(right)
        elif node.op_tok.type == T_POW:
            result, error = left.to_pow_of(right)
        elif node.op_tok.type == T_EE:
            result, error = left.get_comparison_equals(right)
        elif node.op_tok.type == T_NE:
            result, error = left.get_comparison_notequals(right)
        elif node.op_tok.type == T_LE:
            result, error = left.get_comparison_lessthan(right)
        elif node.op_tok.type == T_GE:
            result, error = left.get_comparison_greaterthan(right)
        elif node.op_tok.type == T_LTE:
            result, error = left.get_comparison_lessthanequals(right)
        elif node.op_tok.type == T_GTE:
            result, error = left.get_comparison_greaterthanequals(right)
        elif node.op_tok.matches(T_KEYWORD, 'and'):
            result, error = left.and_with(right)
        elif node.op_tok.matches(T_KEYWORD, 'or'):
            result, error = left.or_with(right)


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
        if node.op_tok.matches(T_KEYWORD, "not"):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))
    
    def visit_IfNode(self, node, context):
        res = RTResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error: return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error: return res
                return res.success(expr_value)
            
        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error: return res
            return res.success(else_value)
        
        return res.success(None)
    
    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error: return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error: return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error: return res
        else:
            step_value = Number(1)
        
        i = start_value.value
        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            elements.append(res.register(self.visit(node.body_node, context)))
            if res.error: return res
        
        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_WhileNode(self, node, context):
        res = RTResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error: return res

            if not condition.is_true(): break

            elements.append(res.register(self.visit(node.body_node, context)))
            if res.error: return res

        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_FuncDefNode(self, node, context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_start, node.pos_end)

        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)
        
        return res.success(func_value)
    
    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.error: return res

        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error: return res
        
        return_value = res.register(value_to_call.execute(args))
        if res.error: return res
        return res.success(return_value)

### RUN

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number.null)
global_symbol_table.set("true", Number.false)
global_symbol_table.set("false", Number.true)
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