from bits.nodes import *
from bits.error import *
from bits.constants import *
from bits.results import ParseResult

### PARSER

class Parser:
    def __init__(self, tokens):
        self.toks = tokens
        self.tok_index = -1
        self.next()
    
    def next(self):
        self.tok_index += 1
        self.update_current_tok()
        return self.current_tok
    
    def reverse(self, amount=1):
        self.tok_index -= amount
        self.update_current_tok()
        return self.current_tok
    
    def update_current_tok(self):
        if self.tok_index >= 0 and self.tok_index < len(self.toks):
            self.current_tok = self.toks[self.tok_index]
    
    def parse(self):
        res = self.statements()
        if not res.error and self.current_tok.type != T_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '+', '-', '*', '/', '//', '^', '==', '!=', '<', '>', <=', '>=', 'and' or 'or'"
            ))
        return res
    
    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == T_NEWLINE:
            res.register_next()
            self.next()

        statement = res.register(self.expr())
        if res.error: return res
        statements.append(statement)

        more = True

        while True:
            newline_c = 0
            while self.current_tok.type == T_NEWLINE:
                res.register_next()
                self.next()
                newline_c += 1
            if newline_c == 0:
                more = False
            
            if not more: break
            statement = res.try_register(self.expr())
            if not statement:
                self.reverse(res.to_reverse_count)
                more = False
                continue
            statements.append(statement)
        
        return res.success(ListNode(
            statements, pos_start, self.current_tok.pos_end.copy()
        ))
    
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
        all_cases = res.register(self.if_expr_cases("if"))
        if res.error: return res

        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))
    
    def if_expr_b(self):
        return self.if_expr_cases('elif')
    
    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(T_KEYWORD, 'else'):
            res.register_next()
            self.next()

            if self.current_tok.type == T_NEWLINE:
                res.register_next()
                self.next()

                statements = res.register(self.statements())
                if res.error: return res
                else_case = (statements, True)

                if self.current_tok.matches(T_KEYWORD, 'end'):
                    res.register_next()
                    self.next()
                else:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected 'end'"
                    ))
            else:
                expr = res.register(self.expr())
                if res.error: return res
                else_case = (expr, False)
        
        return res.success(else_case)
    
    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_tok.matches(T_KEYWORD, "elif"):
            all_cases = res.register(self.if_expr_b())
            if res.error: return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error: return res
        
        return res.success((cases, else_case))
    
    def if_expr_cases(self, keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(T_KEYWORD, keyword):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{keyword}'"
            ))
        
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

        if self.current_tok.type == T_NEWLINE:
            res.register_next()
            self.next()

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))

            if self.current_tok.matches(T_KEYWORD, 'end'):
                res.register_next()
                self.next()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error: return res

                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.expr())
            if res.error: return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))
    
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

        if self.current_tok.type == T_NEWLINE:
            res.register_next()
            self.next()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.matches(T_KEYWORD, 'end'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected 'end'"
                ))
            
            res.register_next()
            self.next()

            return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = res.register(self.expr())
        if res.error: return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))
    
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

        res.register_next()
        self.next()

        if not self.current_tok.matches(T_KEYWORD, 'do'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'do'"
            )) 
        
        if self.current_tok.type == T_NEWLINE:
            res.register_next()
            self.next()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.matches(T_KEYWORD, 'end'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected 'end'"
                ))
            
            res.register_next()
            self.next()

            return res.success(WhileNode(condition, body, True))

        body = res.register(self.expr())
        if res.error: return res

        return res.success(WhileNode(condition, body, False))

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

        if self.current_tok.type == T_ARROW:
            res.register_next()
            self.next()

            node_to_return = res.register(self.expr())
            if res.error: return res

            return res.success(FuncDefNode(var_name_tok, arg_name_toks, node_to_return, False))
        
        if self.current_tok.type != T_NEWLINE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '->' or NEWLINE"
            ))
        
        res.register_next()
        self.next()

        body = res.register(self.statements())
        if res.error: return res

        if not self.current_tok.matches(T_KEYWORD, 'end'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'end'"
            ))
        
        res.register_next()
        self.next()

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, body, True))
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