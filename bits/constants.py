import string

DIGITS = "0123456789"
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS + "_"

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