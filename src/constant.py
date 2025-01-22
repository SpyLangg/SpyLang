import string

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_STRING = "STRING"
TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_NEWLINE = "NEWLINE"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_EOF = "EOF"
TT_POW = "POW"
TT_EQ = "EQ"
TT_EE = 'EE'
TT_NE = 'NE'
TT_LT = 'LT'
TT_GT = 'GT'
TT_LTE = "LTE"
TT_GTE = 'GTE'
TT_ARROW = 'ARROW'
TT_COMMA = 'COMMA'
TT_DOT='DOT'
TT_LSQUARE = 'LSQUARE'
TT_RSQUARE = 'RSQUARE'
TT_LCURLY = 'LCURLY'
TT_RCURLY = 'RCURLY'
TT_RANGE = "RANGE"
TT_MOD='MOD'
TT_SEMICOL = "SEMICOL"


KEYWORDS = [
    'assign',
    'and',    
    'or',    
    'not',    
    'check',
    'followup',
    'otherwise',
    'each',      
    'mission',  
    'chase',
    'extract',
    'in',
    'proceed',
    'abort', 
]