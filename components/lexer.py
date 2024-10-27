from bits.position import *
from bits.token import *
from bits.error import *
from bits.constants import *

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
            
            # string
            elif self.current_char == '"':
                tok, error = self.make_string('"')
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == "'":
                tok, error = self.make_string("'")
                if error: return [], error
                tokens.append(tok)

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
    
    def make_string(self, start_char='"'):
        string = ''
        pos_start = self.pos.copy()
        escape_char = False
        self.next()

        escape_chars = {
            'n' : '\n',
            't' : '\t'
        }

        while self.current_char != None and (self.current_char != start_char or escape_char):
            if escape_char:
                string += escape_chars.get(self.current_char, self.current_char)
                escape_char = False
            else:
                if self.current_char == '\\':
                    escape_char = True
                else:
                    string += self.current_char
            self.next()

        if self.current_char == start_char:    
            self.next()
            return Token(T_STRING, string, pos_start, self.pos), None
        else:
            return None, ExpectedCharError(
                pos_start, self.pos,
                f'{start_char}'
            )
    
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