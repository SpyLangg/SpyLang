from strings_with_arrow import *
import string
import os
import math
import sys
import Shell

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

##############################################################################
# ERRORS
#############################################################################

class Error:
    """
    Base class for all error types in SpyLang.
    
    Attributes:
        pos_start (Position): The starting position of the error in the source code.
        pos_end (Position): The ending position of the error in the source code.
        error_name (str): The name of the error.
        details (str): Additional details about the error.
    """
    def __init__(self, pos_start, pos_end, error_name, details):
        """
        Initializes a new error instance.
        
        Args:
            pos_start (Position): The starting position of the error.
            pos_end (Position): The ending position of the error.
            error_name (str): The name of the error.
            details (str): Additional details about the error.
        """
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        """
        Returns a string representation of the error.
        
        Returns:
            str: A formatted string describing the error.
        """
        result = f"{self.error_name}:{self.details}"
        result += f"File{self.pos_start.fn},line{self.pos_start.ln+1}"
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    """
    Error raised when an illegal character is encountered.
    """
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Agent Error: Unauthorized character detected in the operation. Mission compromised!", details)

class ExpectedCharError(Error):
    """
    Error raised when an expected character is not found.
    """
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Agent Error: Expected character not found in the operation. Mission compromised!", details)

class KeyboardInterruptError(Error):
    """
    Error raised when the user manually interrupts the program.
    """
    def __init__(self, pos_start=None, pos_end=None, details="The operation was manually aborted by the agent."):
        super().__init__(pos_start, pos_end, "Agent Error: Manual Termination Detected", details)


class InvalidSyntaxError(Error):
    """
    Error raised when invalid syntax is encountered.
    """
    def __init__(self, pos_start, pos_end, details=""):
        super().__init__(pos_start, pos_end, "Agent Error: Syntax anomaly encountered. The mission is incomplete.", details)

class RTError(Error):
    """
    Error raised during runtime.
    
    Attributes:
        context (Context): The context in which the error occurred.
    """
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, "Agent Error: Runtime breach! Unauthorized behavior detected in the system.", details)
        self.context = context

    def as_string(self):
        """
        Returns a string representation of the runtime error, including the traceback.
        
        Returns:
            str: A formatted string describing the error and its traceback.
        """
        result = self.generate_traceback()
        result += f"Agent Error: Mission failure detected. {self.error_name}: {self.details}. The operation cannot proceed."
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        """
        Generates a traceback for the error.
        
        Returns:
            str: A formatted string representing the traceback.
        """
        result = ""
        pos = self.pos_start
        ctx = self.context
        
        while ctx:
            result = f'Mission Log: File "{pos.fn}", line {str(pos.ln + 1)}, in {ctx.display_name}\n ' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        
        return 'Mission Traceback (Most Recent Incident Last):\n' + result


##################################################################
# POSITION
#################################################################

class Position:
    """
    Represents a position in the source code.
    
    Attributes:
        idx (int): The index in the source code.
        ln (int): The line number.
        col (int): The column number.
        fn (str): The filename.
        ftxt (str): The full text of the source code.
    """
    def __init__(self, idx, ln, col, fn, ftxt):
        """
        Initializes a new position instance.
        
        Args:
            idx (int): The index in the source code.
            ln (int): The line number.
            col (int): The column number.
            fn (str): The filename.
            ftxt (str): The full text of the source code.
        """
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        """
        Advances the position by one character.
        
        Args:
            current_char (str): The current character. Defaults to None.
        
        Returns:
            Position: The updated position.
        """
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        """
        Creates a copy of the current position.
        
        Returns:
            Position: A new position instance with the same attributes.
        """
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

######################################################################
# TOKENS
######################################################################

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

class Token:
    """
    Represents a single token in the SpyLang language, which can be an identifier, keyword, or operator.
    
    Attributes:
        type_ (str): The type of the token (e.g., INT, FLOAT, IDENTIFIER, KEYWORD).
        value (any): The value of the token (e.g., a number or string).
        pos_start (Position): The starting position of the token in the source code.
        pos_end (Position): The ending position of the token in the source code.
    """
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        """
        Initializes a new token instance.
        
        Args:
            type_ (str): The type of the token.
            value (any): The value of the token. Defaults to None.
            pos_start (Position): The starting position. Defaults to None.
            pos_end (Position): The ending position. Defaults to None.
        """
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, type_, value):
        """
        Checks if the token matches a given type and value.
        
        Args:
            type_ (str): The type to match.
            value (any): The value to match.
        
        Returns:
            bool: True if the token matches, False otherwise.
        """
        return self.type == type_ and self.value == value
    
    def __repr__(self):
        """
        Returns a string representation of the token.
        
        Returns:
            str: A formatted string describing the token.
        """
        if self.value:
            return f"Agent Report: {self.type} - Code: {self.value}"
        return f"Agent Status: {self.type} - No Value Assigned"

###################################################################################
# LEXER
#####################################################################################

class Lexer:
    """
    The lexer class is responsible for converting the source code into tokens.
    
    Attributes:
        fn (str): The filename of the source code.
        text (str): The source code text.
        pos (Position): The current position in the source code.
        current_char (str): The current character being processed.
    """
    def __init__(self, fn, text):
        """
        Initializes a new lexer instance.
        
        Args:
            fn (str): The filename of the source code.
            text (str): The source code text.
        """
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        """
        Advances the position to the next character in the source code.
        """
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        """
        Converts the source code into a list of tokens.
        
        Returns:
            list: A list of tokens.
            Error: An error if one occurs during tokenization.
        """
        tokens = []
        while self.current_char != None:
            if self.current_char in " \t":
                self.advance()
            elif self.current_char == ".":
                pos_start = self.pos.copy()
                if self.current_char == ".":
                    tokens.append(Token(TT_RANGE, pos_start=pos_start, pos_end=self.pos))
                    self.advance()
      
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
         
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '\n':
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
           
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '"':
                tokens.append(self.make_string())
            elif self.current_char == "*":
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == "%":
                tokens.append(Token(TT_MOD, pos_start=self.pos))
                self.advance()
            elif self.current_char == "^":
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()

            elif self.current_char == "#":
                self.skip_comment()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == "[":
                tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == "]":
                tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '!':
                tok, error = self.make_not_equals()
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == "{":
                tokens.append(Token(TT_LCURLY, pos_start=self.pos))
                self.advance()
            elif self.current_char == "}":
                tokens.append(Token(TT_RCURLY, pos_start=self.pos))
                self.advance()
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            elif self.current_char == ",":
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        """
        Creates a number token (integer or float) from the source code.
        
        Returns:
            Token: A token representing the number.
        """
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        if self.current_char == '-':
            num_str += '-'
            self.advance()

        while self.current_char is not None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

    def make_identifier(self):
        """
        Creates an identifier or keyword token from the source code.
        
        Returns:
            Token: A token representing the identifier or keyword.
        """
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in LETTERS_DIGITS + "_":
            id_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_not_equals(self):
        """
        Creates a not-equals token from the source code.
        
        Returns:
            Token: A token representing the not-equals operator.
            Error: An error if one occurs during tokenization.
        """
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == "=":
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None
        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def make_equals(self):
        """
        Creates an equals or double-equals token from the source code.
        
        Returns:
            Token: A token representing the equals or double-equals operator.
        """
        tok_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = TT_EE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_range_operator(self):
        """
        Creates a range operator token from the source code.
        
        Returns:
            Token: A token representing the range operator.
            Error: An error if one occurs during tokenization.
        """
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '.':
            self.advance()
            return Token(TT_RANGE, pos_start=pos_start, pos_end=self.pos), None
        return None, IllegalCharError(pos_start, self.pos, "'.'")

    def make_less_than(self):
        """
        Creates a less-than or less-than-equals token from the source code.
        
        Returns:
            Token: A token representing the less-than or less-than-equals operator.
        """
        tok_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        """
        Creates a greater-than or greater-than-equals token from the source code.
        
        Returns:
            Token: A token representing the greater-than or greater-than-equals operator.
        """
        tok_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def peek(self):
        """
        Peeks at the next character in the source code without advancing the position.
        
        Returns:
            str: The next character in the source code.
        """
        if self.pos.idx + 1 < len(self.text):
            return self.text[self.pos.idx + 1]
        return None

    def make_string(self):
        """
        Creates a string token from the source code.
        
        Returns:
            Token: A token representing the string.
        """
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n': "\n",
            't': '\t'
        }

        while self.current_char != None and self.current_char != '"' or escape_character:
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()
            escape_character = False

        self.advance()
        return Token(TT_STRING, string, pos_start, self.pos)
    
    def skip_comment(self):
        """
        Skips a comment in the source code.
        """
        self.advance()
        while self.current_char != '\n':
            self.advance()
        self.advance()

###########################################################################
# NODES
###########################################################################

class NumberNode:
    """
    Represents a number node in the abstract syntax tree (AST).
    
    Attributes:
        tok (Token): The token representing the number.
        pos_start (Position): The starting position of the number in the source code.
        pos_end (Position): The ending position of the number in the source code.
    """
    def __init__(self, tok):
        """
        Initializes a new number node instance.
        
        Args:
            tok (Token): The token representing the number.
        """
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        """
        Returns a string representation of the number node.
        
        Returns:
            str: A formatted string describing the number node.
        """
        return f'{self.tok}'

class StringNode:
    """
    Represents a string node in the abstract syntax tree (AST).
    
    Attributes:
        tok (Token): The token representing the string.
        pos_start (Position): The starting position of the string in the source code.
        pos_end (Position): The ending position of the string in the source code.
    """
    def __init__(self, tok):
        """
        Initializes a new string node instance.
        
        Args:
            tok (Token): The token representing the string.
        """
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        """
        Returns a string representation of the string node.
        
        Returns:
            str: A formatted string describing the string node.
        """
        return f'{self.tok}'

class ListNode:
    """
    Represents a list node in the abstract syntax tree (AST).
    
    Attributes:
        element_nodes (list): A list of element nodes in the list.
        pos_start (Position): The starting position of the list in the source code.
        pos_end (Position): The ending position of the list in the source code.
    """
    def __init__(self, element_nodes, pos_start, pos_end):
        """
        Initializes a new list node instance.
        
        Args:
            element_nodes (list): A list of element nodes in the list.
            pos_start (Position): The starting position of the list.
            pos_end (Position): The ending position of the list.
        """
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end

class RangeNode:
    """
    Represents a range node in the abstract syntax tree (AST).
    
    Attributes:
        start_node (Node): The starting node of the range.
        end_node (Node): The ending node of the range.
        pos_start (Position): The starting position of the range in the source code.
        pos_end (Position): The ending position of the range in the source code.
    """
    def __init__(self, start_node, end_node):
        """
        Initializes a new range node instance.
        
        Args:
            start_node (Node): The starting node of the range.
            end_node (Node): The ending node of the range.
        """
        self.start_node = start_node
        self.end_node = end_node
        self.pos_start = self.start_node.pos_start
        self.pos_end = self.end_node.pos_end

class VarAccessNode:
    """
    Represents a variable access node in the abstract syntax tree (AST).
    
    Attributes:
        var_name_tok (Token): The token representing the variable name.
        pos_start (Position): The starting position of the variable in the source code.
        pos_end (Position): The ending position of the variable in the source code.
    """
    def __init__(self, var_name_tok):
        """
        Initializes a new variable access node instance.
        
        Args:
            var_name_tok (Token): The token representing the variable name.
        """
        self.var_name_tok = var_name_tok
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

class VarAssignNode:
    """
    Represents a variable assignment node in the abstract syntax tree (AST).
    
    Attributes:
        var_name_tok (Token): The token representing the variable name.
        value_node (Node): The node representing the value to be assigned.
        pos_start (Position): The starting position of the assignment in the source code.
        pos_end (Position): The ending position of the assignment in the source code.
    """
    def __init__(self, var_name_tok, value_node):
        """
        Initializes a new variable assignment node instance.
        
        Args:
            var_name_tok (Token): The token representing the variable name.
            value_node (Node): The node representing the value to be assigned.
        """
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end

class BinOpNode:
    """
    Represents a binary operation node in the abstract syntax tree (AST).
    
    Attributes:
        left_node (Node): The left operand node.
        op_tok (Token): The token representing the operator.
        right_node (Node): The right operand node.
        pos_start (Position): The starting position of the operation in the source code.
        pos_end (Position): The ending position of the operation in the source code.
    """
    def __init__(self, left_node, op_tok, right_node):
        """
        Initializes a new binary operation node instance.
        
        Args:
            left_node (Node): The left operand node.
            op_tok (Token): The token representing the operator.
            right_node (Node): The right operand node.
        """
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        """
        Returns a string representation of the binary operation node.
        
        Returns:
            str: A formatted string describing the binary operation node.
        """
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
    """
    Represents a unary operation node in the abstract syntax tree (AST).
    
    Attributes:
        op_tok (Token): The token representing the operator.
        node (Node): The operand node.
        pos_start (Position): The starting position of the operation in the source code.
        pos_end (Position): The ending position of the operation in the source code.
    """
    def __init__(self, op_tok, node):
        """
        Initializes a new unary operation node instance.
        
        Args:
            op_tok (Token): The token representing the operator.
            node (Node): The operand node.
        """
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        """
        Returns a string representation of the unary operation node.
        
        Returns:
            str: A formatted string describing the unary operation node.
        """
        return f'({self.op_tok}, {self.node})'

class IfNode:
    """
    Represents an if statement node in the abstract syntax tree (AST).
    
    Attributes:
        cases (list): A list of tuples representing the if and followup cases.
        else_case (list): A list of nodes representing the else case.
        pos_start (Position): The starting position of the if statement in the source code.
        pos_end (Position): The ending position of the if statement in the source code.
    """
    def __init__(self, cases, else_case=None):
        """
        Initializes a new if statement node instance.
        
        Args:
            cases (list): A list of tuples representing the if and followup cases.
            else_case (list): A list of nodes representing the else case. Defaults to an empty list.
        """
        self.cases = cases
        self.else_case = else_case or []  
        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (
            self.else_case[-1].pos_end if self.else_case and hasattr(self.else_case[-1], 'pos_end')
            else self.cases[-1][1].pos_end
        )

class ForNode:
    """
    Represents a for loop node in the abstract syntax tree (AST).
    
    Attributes:
        var_name_tok (Token): The token representing the loop variable name.
        start_value_node (Node): The node representing the start value of the loop.
        end_value_node (Node): The node representing the end value of the loop.
        step_value_node (Node): The node representing the step value of the loop.
        body_node (Node): The node representing the body of the loop.
        should_return_null (bool): Whether the loop should return null.
        pos_start (Position): The starting position of the for loop in the source code.
        pos_end (Position): The ending position of the for loop in the source code.
    """
    def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
        """
        Initializes a new for loop node instance.
        
        Args:
            var_name_tok (Token): The token representing the loop variable name.
            start_value_node (Node): The node representing the start value of the loop.
            end_value_node (Node): The node representing the end value of the loop.
            step_value_node (Node): The node representing the step value of the loop.
            body_node (Node): The node representing the body of the loop.
            should_return_null (bool): Whether the loop should return null.
        """
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

class WhileNode:
    """
    Represents a while loop node in the abstract syntax tree (AST).
    
    Attributes:
        condition_node (Node): The node representing the loop condition.
        body_node (Node): The node representing the body of the loop.
        should_return_null (bool): Whether the loop should return null.
        pos_start (Position): The starting position of the while loop in the source code.
        pos_end (Position): The ending position of the while loop in the source code.
    """
    def __init__(self, condition_node, body_node, should_return_null):
        """
        Initializes a new while loop node instance.
        
        Args:
            condition_node (Node): The node representing the loop condition.
            body_node (Node): The node representing the body of the loop.
            should_return_null (bool): Whether the loop should return null.
        """
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null
        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

class FuncDefNode:
    """
    Represents a function definition node in the abstract syntax tree (AST).
    
    Attributes:
        var_name_tok (Token): The token representing the function name.
        arg_name_toks (list): A list of tokens representing the function arguments.
        body_node (Node): The node representing the body of the function.
        should_auto_return (bool): Whether the function should automatically return a value.
        pos_start (Position): The starting position of the function definition in the source code.
        pos_end (Position): The ending position of the function definition in the source code.
    """
    def __init__(self, var_name_tok, arg_name_toks, body_node, should_auto_return):
        """
        Initializes a new function definition node instance.
        
        Args:
            var_name_tok (Token): The token representing the function name.
            arg_name_toks (list): A list of tokens representing the function arguments.
            body_node (Node): The node representing the body of the function.
            should_auto_return (bool): Whether the function should automatically return a value.
        """
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.should_auto_return = should_auto_return

        if self.var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end

class CallNode:
    """
    Represents a function call node in the abstract syntax tree (AST).
    
    Attributes:
        node_to_call (Node): The node representing the function to be called.
        arg_nodes (list): A list of nodes representing the function arguments.
        pos_start (Position): The starting position of the function call in the source code.
        pos_end (Position): The ending position of the function call in the source code.
    """
    def __init__(self, node_to_call, arg_nodes):
        """
        Initializes a new function call node instance.
        
        Args:
            node_to_call (Node): The node representing the function to be called.
            arg_nodes (list): A list of nodes representing the function arguments.
        """
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes
        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end

class ReturnNode:
    """
    Represents a return statement node in the abstract syntax tree (AST).
    
    Attributes:
        node_to_return (Node): The node representing the value to be returned.
        pos_start (Position): The starting position of the return statement in the source code.
        pos_end (Position): The ending position of the return statement in the source code.
    """
    def __init__(self, node_to_return, pos_start, pos_end):
        """
        Initializes a new return statement node instance.
        
        Args:
            node_to_return (Node): The node representing the value to be returned.
            pos_start (Position): The starting position of the return statement.
            pos_end (Position): The ending position of the return statement.
        """
        self.node_to_return = node_to_return
        self.pos_start = pos_start
        self.pos_end = pos_end

class ContinueNode:
    """
    Represents a continue statement node in the abstract syntax tree (AST).
    
    Attributes:
        pos_start (Position): The starting position of the continue statement in the source code.
        pos_end (Position): The ending position of the continue statement in the source code.
    """
    def __init__(self, pos_start, pos_end):
        """
        Initializes a new continue statement node instance.
        
        Args:
            pos_start (Position): The starting position of the continue statement.
            pos_end (Position): The ending position of the continue statement.
        """
        self.pos_start = pos_start
        self.pos_end = pos_end

class BreakNode:
    """
    Represents a break statement node in the abstract syntax tree (AST).
    
    Attributes:
        pos_start (Position): The starting position of the break statement in the source code.
        pos_end (Position): The ending position of the break statement in the source code.
    """
    def __init__(self, pos_start, pos_end):
        """
        Initializes a new break statement node instance.
        
        Args:
            pos_start (Position): The starting position of the break statement.
            pos_end (Position): The ending position of the break statement.
        """
        self.pos_start = pos_start
        self.pos_end = pos_end

########################################################
# PARSE RESULT
#######################################################

class ParseResult:
    """
    Represents the result of parsing a piece of source code.
    
    Attributes:
        error (Error): The error encountered during parsing, if any.
        node (Node): The root node of the parsed abstract syntax tree (AST).
        last_registered_advance_count (int): The number of tokens advanced during the last registered operation.
        advance_count (int): The total number of tokens advanced during parsing.
        to_reverse_count (int): The number of tokens to reverse if an error occurs.
    """
    def __init__(self):
        """
        Initializes a new parse result instance.
        """
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        """
        Registers an advancement in the token stream.
        """
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def register(self, res):
        """
        Registers a parse result.
        
        Args:
            res (ParseResult): The parse result to register.
        
        Returns:
            Node: The node from the registered parse result.
        """
        self.last_registered_advance_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node

    def try_register(self, res):
        """
        Tries to register a parse result, reversing the token stream if an error occurs.
        
        Args:
            res (ParseResult): The parse result to try to register.
        
        Returns:
            Node: The node from the registered parse result, or None if an error occurs.
        """
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def success(self, node):
        """
        Marks the parse result as successful.
        
        Args:
            node (Node): The root node of the parsed abstract syntax tree (AST).
        
        Returns:
            ParseResult: The updated parse result.
        """
        self.node = node
        return self

    def failure(self, error):
        """
        Marks the parse result as a failure.
        
        Args:
            error (Error): The error encountered during parsing.
        
        Returns:
            ParseResult: The updated parse result.
        """
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self

###########################################################################
# PARSER
################################################################################

class Parser:
    """
    The parser class is responsible for converting a list of tokens into an abstract syntax tree (AST).
    
    Attributes:
        tokens (list): The list of tokens to parse.
        tok_idx (int): The current index in the token list.
        current_tok (Token): The current token being processed.
    """
    def __init__(self, tokens):
        """
        Initializes a new parser instance.
        
        Args:
            tokens (list): The list of tokens to parse.
        """
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        """
        Advances to the next token in the token list.
        
        Returns:
            Token: The updated current token.
        """
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        """
        Reverses the token stream by a specified amount.
        
        Args:
            amount (int): The number of tokens to reverse. Defaults to 1.
        
        Returns:
            Token: The updated current token.
        """
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        """
        Updates the current token based on the current index in the token list.
        """
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def range_expr(self):
        """
        Parses a range expression from the token list.
        
        Returns:
            ParseResult: The result of parsing the range expression.
        """
        res = ParseResult()

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()

        start_value = res.register(self.arith_expr())
        if res.error: return res

        if self.current_tok.type != TT_RANGE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '..' for range"
            ))

        res.register_advancement()
        self.advance()

        end_value = res.register(self.arith_expr())
        if res.error: return res

        if self.current_tok.type == TT_RPAREN:
            res.register_advancement()
            self.advance()

        return res.success(RangeNode(start_value, end_value))

    def parse(self):
        """
        Parses the token list into an abstract syntax tree (AST).
        
        Returns:
            ParseResult: The result of parsing the token list.
        """
        res = self.statements()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Unexpected token: {self.current_tok}"
            ))
        return res

    ###################################

    def statements(self):
        """
        Parses a series of statements from the token list.
        
        Returns:
            ParseResult: The result of parsing the statements.
        """
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        while self.current_tok.type == TT_NEWLINE:
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                break
            statements.append(statement)

        return res.success(ListNode(statements, pos_start, self.current_tok.pos_end.copy()))

    def statement(self):
        """
        Parses a single statement from the token list.
        
        Returns:
            ParseResult: The result of parsing the statement.
        """
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.matches(TT_KEYWORD, 'extract'):
            res.register_advancement()
            self.advance()

            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))
        
        if self.current_tok.matches(TT_KEYWORD, 'proceed'):
            res.register_advancement()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))
            
        if self.current_tok.matches(TT_KEYWORD, 'abort'):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

        expr = res.register(self.expr())
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'extract', 'proceed', 'abort', 'assign', 'check', 'each', 'chase', 'mission', int, float, identifier, '+', '-', '(', '[' or 'not'"
            ))
        return res.success(expr)

    def expr(self):
        """
        Parses an expression from the token list.
        
        Returns:
            ParseResult: The result of parsing the expression.
        """
        res = ParseResult()


        if self.current_tok.matches(TT_KEYWORD, 'assign'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier after 'assign'"
                ))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '=' after variable name"
                ))

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res

            return res.success(VarAssignNode(var_name, expr))

      
        if self.current_tok.type == TT_IDENTIFIER:
            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TT_EQ:
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                if res.error:
                    return res
                return res.success(VarAssignNode(var_name, expr))

            
            self.reverse()

      
        node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'assign', 'check', 'each', 'chase', 'mission', int, float, identifier, '+', '-', '(', '[' or 'not'"
            ))

        return res.success(node)

    def comp_expr(self):
        """
        Parses a comparison expression from the token list.
        
        Returns:
            ParseResult: The result of parsing the comparison expression.
        """
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'not'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))
        
        node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))
        
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected int, float, identifier, '+', '-', '(', '[', 'check', 'each', 'chase', 'mission' or 'not'"
            ))

        return res.success(node)

    def arith_expr(self):
        """
        Parses an arithmetic expression from the token list.
        
        Returns:
            ParseResult: The result of parsing the arithmetic expression.
        """
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def term(self):
        """
        Parses a term from the token list.
        
        Returns:
            ParseResult: The result of parsing the term.
        """
        return self.bin_op(self.factor, (TT_MUL, TT_DIV,TT_MOD))

    def factor(self):
        """
        Parses a factor from the token list.
        
        Returns:
            ParseResult: The result of parsing the factor.
        """
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):  
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def power(self):
        """
        Parses a power expression from the token list.
        
        Returns:
            ParseResult: The result of parsing the power expression.
        """
        return self.bin_op(self.call, (TT_POW, ), self.factor)

    def call(self):
        """
        Parses a function call from the token list.
        
        Returns:
            ParseResult: The result of parsing the function call.
        """
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error: return res

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ',' or ')'"
                    ))

                res.register_advancement()
                self.advance()

            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def atom(self):
        """
        Parses an atom (basic unit) from the token list.
        
        Returns:
            ParseResult: The result of parsing the atom.
        """
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))
        
        elif self.current_tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return self.range_expr() if self.peek() == TT_RANGE else super().atom()

        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))

        elif tok.type == TT_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error: return res
            return res.success(list_expr)
        
        elif tok.matches(TT_KEYWORD, 'check'):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        elif tok.matches(TT_KEYWORD, 'each'):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)

        elif tok.matches(TT_KEYWORD, 'chase'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)

        elif tok.matches(TT_KEYWORD, 'mission'):
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, identifier, '+', '-', '(', '[', check', 'each', 'chase', 'mission'"
        ))


    def list_expr(self):
        """
        Parses a list expression from the token list.
        
        Returns:
            ParseResult: The result of parsing the list expression.
        """
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT_LSQUARE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '['"
        ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error: return res

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                element_nodes.append(res.register(self.expr()))
                if res.error: return res

            if self.current_tok.type != TT_RSQUARE:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ',' or ']'"
                ))

            res.register_advancement()
            self.advance()

        return res.success(ListNode(element_nodes, pos_start, self.current_tok.pos_end.copy()))


    def if_expr(self):
        """
        Parses an if statement from the token list.
        
        Returns:
            ParseResult: The result of parsing the if statement.
        """
        res = ParseResult()

      
        if not self.current_tok.matches(TT_KEYWORD, 'check'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'check'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{' to start block"
            ))

        res.register_advancement()
        self.advance()

       
        body = res.register(self.statements())
        if res.error: return res

        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}' to end block"
            ))

        res.register_advancement()
        self.advance()

        
        followups = []
        else_case = None

        while self.current_tok.matches(TT_KEYWORD, 'followup'):
            res.register_advancement()
            self.advance()

            followup_condition = res.register(self.expr())
            if res.error: return res

            if self.current_tok.type != TT_LCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '{' to start block"
                ))

            res.register_advancement()
            self.advance()

            followup_body = res.register(self.statements())
            if res.error: return res

            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}' to end block"
                ))

            res.register_advancement()
            self.advance()
            followups.append((followup_condition, followup_body, False))
            

        if self.current_tok.matches(TT_KEYWORD, 'otherwise'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_LCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '{' to start block"
                ))

            res.register_advancement()
            self.advance()

            else_case_node = res.register(self.statements())
            if res.error: return res

            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}' to end block"
                ))

            res.register_advancement()
            self.advance()
            else_case = else_case_node.element_nodes if isinstance(else_case_node, ListNode) else []

        return res.success(IfNode([(condition, body, True)] + followups, else_case))

    def if_expr_b(self):
        """
        Parses a followup case in an if statement from the token list.
        
        Returns:
            ParseResult: The result of parsing the followup case.
        """
        return self.if_expr_cases('followup')
    
    def if_expr_c(self):
        """
        Parses an otherwise case in an if statement from the token list.
        
        Returns:
            ParseResult: The result of parsing the otherwise case.
        """
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(TT_KEYWORD, 'otherwise'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_LCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '{' to open block"
                ))

            res.register_advancement()
            self.advance()


            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            body = res.register(self.statements())
            if res.error: return res

        
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}' to close block"
                ))

            res.register_advancement()
            self.advance()
            else_case = (body, True)

        return res.success(else_case)

    def if_expr_b_or_c(self):
        """
        Parses followup and otherwise cases in an if statement from the token list.
        
        Returns:
            ParseResult: The result of parsing the followup and otherwise cases.
        """
        res = ParseResult()
        cases, else_case = [], None

        
        while self.current_tok.matches(TT_KEYWORD, 'followup'):
            res.register_advancement()
            self.advance()

            condition = res.register(self.expr())
            if res.error: return res

            if self.current_tok.type != TT_LCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '{' to open block"
                ))

            res.register_advancement()
            self.advance()

            
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            body = res.register(self.statements())
            if res.error: return res

            
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}' to close block"
                ))

            res.register_advancement()
            self.advance()
            cases.append((condition, body, True))

        
        if self.current_tok.matches(TT_KEYWORD, 'otherwise'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_LCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '{' to open block"
                ))

            res.register_advancement()
            self.advance()


            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            else_body = res.register(self.statements())
            if res.error: return res

            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}' to close block"
                ))

            res.register_advancement()
            self.advance()
            else_case = (else_body, True)

        return res.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        """
        Parses cases in an if statement from the token list.
        
        Args:
            case_keyword (str): The keyword representing the case (e.g., 'followup').
        
        Returns:
            ParseResult: The result of parsing the cases.
        """
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT_KEYWORD, case_keyword):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{case_keyword}'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Invalid condition in 'check' statement"
        ))

        
        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{' to start the block"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))

            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}' to close the block"
                ))

            res.register_advancement()
            self.advance()

        else:
            expr = res.register(self.statement())
            if res.error: return res
            cases.append((condition, expr, False))

        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}' to close the block"
            ))

        res.register_advancement()
        self.advance()

        
        all_cases = res.register(self.if_expr_b_or_c())
        if res.error: return res
        new_cases, else_case = all_cases
        cases.extend(new_cases)

        return res.success((cases, else_case))

    def for_expr(self):
        """
        Parses a for loop from the token list.
        
        Returns:
            ParseResult: The result of parsing the for loop.
        """
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'each'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'each'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected identifier"
            ))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if not self.current_tok.matches(TT_KEYWORD, 'in'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'in'"
            ))

        res.register_advancement()
        self.advance()

        iterable = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{'"
            ))

        res.register_advancement()
        self.advance()

        body = res.register(self.statements())
        if res.error: return res

        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}'"
            ))

        res.register_advancement()
        self.advance()

        return res.success(ForNode(var_name, iterable, None, None, body, True))

    
    def while_expr(self):
        """
        Parses a while loop from the token list.
        
        Returns:
            ParseResult: The result of parsing the while loop.
        """
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'chase'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'chase'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{' "
            ))

        res.register_advancement()
        self.advance()

        body = None
        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()
            body = res.register(self.statements())
            if res.error: return res
        else:
            body = res.register(self.statement())
            if res.error: return res

        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}' "
            ))

        res.register_advancement()
        self.advance()

        return res.success(WhileNode(condition, body, True))

    def func_def(self):
        """
        Parses a function definition from the token list.
        
        Returns:
            ParseResult: The result of parsing the function definition.
        """
        res = ParseResult()

        
        if not self.current_tok.matches(TT_KEYWORD, 'mission'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'mission'"
            ))

        res.register_advancement()
        self.advance()

    
        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
        else:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected function name"
            ))

        if self.current_tok.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '('"
            ))

        res.register_advancement()
        self.advance()
        arg_name_toks = []

        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected identifier"
                    ))
                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

        if self.current_tok.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ')'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{'"
            ))

        res.register_advancement()
        self.advance()

        body = res.register(self.statements())
        if res.error:
            return res

        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}'"
            ))

        res.register_advancement()
        self.advance()

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, body, False))

    ###################################

    def bin_op(self, func_a, ops, func_b=None):
        """
        Parses a binary operation from the token list.
        
        Args:
            func_a (function): The function to parse the left operand.
            ops (tuple): A tuple of operator types to match.
            func_b (function): The function to parse the right operand. Defaults to func_a.
        
        Returns:
            ParseResult: The result of parsing the binary operation.
        """
        if func_b == None:
            func_b = func_a
        
        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

#######################################################################
# RUNTIME RESULT
#######################################################################

class RTResult:
    """
    Represents the result of evaluating a node during interpretation.
    
    Attributes:
        value (any): The value resulting from the evaluation.
        error (Error): The error encountered during evaluation, if any.
        func_return_value (any): The value to return from a function, if any.
        loop_should_continue (bool): Whether a loop should continue.
        loop_should_break (bool): Whether a loop should break.
    """
    def __init__(self):
        """
        Initializes a new runtime result instance.
        """
        self.reset()

    def reset(self):
        """
        Resets the runtime result to its initial state.
        """
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, res):
        """
        Registers a runtime result.
        
        Args:
            res (RTResult): The runtime result to register.
        
        Returns:
            any: The value from the registered runtime result.
        """
        self.error = res.error
        self.func_return_value = res.func_return_value
        self.loop_should_continue = res.loop_should_continue
        self.loop_should_break = res.loop_should_break
        return res.value

    def success(self, value):
        """
        Marks the runtime result as successful.
        
        Args:
            value (any): The value resulting from the evaluation.
        
        Returns:
            RTResult: The updated runtime result.
        """
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        """
        Marks the runtime result as a successful function return.
        
        Args:
            value (any): The value to return from the function.
        
        Returns:
            RTResult: The updated runtime result.
        """
        self.reset()
        self.func_return_value = value
        return self
    
    def success_continue(self):
        """
        Marks the runtime result as a successful loop continuation.
        
        Returns:
            RTResult: The updated runtime result.
        """
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        """
        Marks the runtime result as a successful loop break.
        
        Returns:
            RTResult: The updated runtime result.
        """
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        """
        Marks the runtime result as a failure.
        
        Args:
            error (Error): The error encountered during evaluation.
        
        Returns:
            RTResult: The updated runtime result.
        """
        self.reset()
        self.error = error
        return self

    def should_return(self):
        """
        Checks if the runtime result should return (due to an error, function return, loop continuation, or loop break).
        
        Returns:
            bool: True if the runtime result should return, False otherwise.
        """
        return (
            self.error or
            self.func_return_value or
            self.loop_should_continue or
            self.loop_should_break
        )

######################################################################
# VALUES
########################################################################

class Value:
    """
    Base class for all values in SpyLang.
    
    Attributes:
        pos_start (Position): The starting position of the value in the source code.
        pos_end (Position): The ending position of the value in the source code.
        context (Context): The context in which the value exists.
    """
    def __init__(self):
        """
        Initializes a new value instance.
        """
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        """
        Sets the position of the value in the source code.
        
        Args:
            pos_start (Position): The starting position. Defaults to None.
            pos_end (Position): The ending position. Defaults to None.
        
        Returns:
            Value: The updated value instance.
        """
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        """
        Sets the context of the value.
        
        Args:
            context (Context): The context in which the value exists. Defaults to None.
        
        Returns:
            Value: The updated value instance.
        """
        self.context = context
        return self

    def added_to(self, other):
        """
        Adds the value to another value.
        
        Args:
            other (Value): The other value to add.
        
        Returns:
            Value: The result of the addition.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        """
        Subtracts another value from the value.
        
        Args:
            other (Value): The other value to subtract.
        
        Returns:
            Value: The result of the subtraction.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        """
        Multiplies the value by another value.
        
        Args:
            other (Value): The other value to multiply.
        
        Returns:
            Value: The result of the multiplication.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        """
        Divides the value by another value.
        
        Args:
            other (Value): The other value to divide.
        
        Returns:
            Value: The result of the division.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        """
        Raises the value to the power of another value.
        
        Args:
            other (Value): The other value to use as the exponent.
        
        Returns:
            Value: The result of the exponentiation.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        """
        Compares the value for equality with another value.
        
        Args:
            other (Value): The other value to compare.
        
        Returns:
            Value: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        """
        Compares the value for inequality with another value.
        
        Args:
            other (Value): The other value to compare.
        
        Returns:
            Value: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        """
        Compares the value for less-than with another value.
        
        Args:
            other (Value): The other value to compare.
        
        Returns:
            Value: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        """
        Compares the value for greater-than with another value.
        
        Args:
            other (Value): The other value to compare.
        
        Returns:
            Value: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        """
        Compares the value for less-than-or-equal-to with another value.
        
        Args:
            other (Value): The other value to compare.
        
        Returns:
            Value: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        """
        Compares the value for greater-than-or-equal-to with another value.
        
        Args:
            other (Value): The other value to compare.
        
        Returns:
            Value: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        """
        Performs a logical AND operation with another value.
        
        Args:
            other (Value): The other value to AND with.
        
        Returns:
            Value: The result of the AND operation.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        """
        Performs a logical OR operation with another value.
        
        Args:
            other (Value): The other value to OR with.
        
        Returns:
            Value: The result of the OR operation.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def notted(self, other):
        """
        Performs a logical NOT operation on the value.
        
        Args:
            other (Value): The other value to NOT.
        
        Returns:
            Value: The result of the NOT operation.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def execute(self, args):
        """
        Executes the value as a function.
        
        Args:
            args (list): The arguments to pass to the function.
        
        Returns:
            RTResult: The result of executing the function.
        """
        return RTResult().failure(self.illegal_operation())

    def copy(self):
        """
        Creates a copy of the value.
        
        Returns:
            Value: A new value instance with the same attributes.
        """
        raise Exception('No copy method defined')

    def is_true(self):
        """
        Checks if the value is considered true.
        
        Returns:
            bool: True if the value is considered true, False otherwise.
        """
        return False

    def illegal_operation(self, other=None):
        """
        Creates an illegal operation error.
        
        Args:
            other (Value): The other value involved in the operation. Defaults to None.
        
        Returns:
            RTError: The illegal operation error.
        """
        if not other: other = self
        return RTError(
            self.pos_start, other.pos_end,
            'Illegal operation',
            self.context
        )

class Number(Value):
    """
    Represents a number value in SpyLang.
    
    Attributes:
        value (float): The numeric value.
    """
    def __init__(self, value):
        """
        Initializes a new number instance.
        
        Args:
            value (float): The numeric value.
        """
        super().__init__()
        self.value = value

    def added_to(self, other):
        """
        Adds the number to another number.
        
        Args:
            other (Number): The other number to add.
        
        Returns:
            Number: The result of the addition.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subbed_by(self, other):
        """
        Subtracts another number from the number.
        
        Args:
            other (Number): The other number to subtract.
        
        Returns:
            Number: The result of the subtraction.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        """
        Multiplies the number by another number.
        
        Args:
            other (Number): The other number to multiply.
        
        Returns:
            Number: The result of the multiplication.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        """
        Divides the number by another number.
        
        Args:
            other (Number): The other number to divide.
        
        Returns:
            Number: The result of the division.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
    def modded_by(self, other):
        """
        Modulus the number by another number.
        
        Args:
            other (Number): The other number to modulus.
        
        Returns:
            Number: The result of the modulus.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Number(self.value % other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        """
        Raises the number to the power of another number.
        
        Args:
            other (Number): The other number to use as the exponent.
        
        Returns:
            Number: The result of the exponentiation.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        """
        Compares the number for equality with another number.
        
        Args:
            other (Number): The other number to compare.
        
        Returns:
            Number: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        """
        Compares the number for inequality with another number.
        
        Args:
            other (Number): The other number to compare.
        
        Returns:
            Number: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        """
        Compares the number for less-than with another number.
        
        Args:
            other (Number): The other number to compare.
        
        Returns:
            Number: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        """
        Compares the number for greater-than with another number.
        
        Args:
            other (Number): The other number to compare.
        
        Returns:
            Number: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        """
        Compares the number for less-than-or-equal-to with another number.
        
        Args:
            other (Number): The other number to compare.
        
        Returns:
            Number: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        """
        Compares the number for greater-than-or-equal-to with another number.
        
        Args:
            other (Number): The other number to compare.
        
        Returns:
            Number: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        """
        Performs a logical AND operation with another number.
        
        Args:
            other (Number): The other number to AND with.
        
        Returns:
            Number: The result of the AND operation.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        """
        Performs a logical OR operation with another number.
        
        Args:
            other (Number): The other number to OR with.
        
        Returns:
            Number: The result of the OR operation.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        """
        Performs a logical NOT operation on the number.
        
        Returns:
            Number: The result of the NOT operation.
            Error: An error if the operation is not supported.
        """
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        """
        Creates a copy of the number.
        
        Returns:
            Number: A new number instance with the same attributes.
        """
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        """
        Checks if the number is considered true.
        
        Returns:
            bool: True if the number is non-zero, False otherwise.
        """
        return self.value != 0

    def __str__(self):
        """
        Returns a string representation of the number.
        
        Returns:
            str: The string representation of the number.
        """
        return str(self.value)
    
    def __repr__(self):
        """
        Returns a string representation of the number.
        
        Returns:
            str: The string representation of the number.
        """
        return str(self.value)

class String(Value):
    """
    Represents a string value in SpyLang.
    
    Attributes:
        value (str): The string value.
    """
    def __init__(self, value):
        """
        Initializes a new string instance.
        
        Args:
            value (str): The string value.
        """
        super().__init__()
        self.value = value

    def added_to(self, other):
        """
        Concatenates the string with another string.
        
        Args:
            other (String): The other string to concatenate.
        
        Returns:
            String: The result of the concatenation.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        """
        Repeats the string a specified number of times.
        
        Args:
            other (Number): The number of times to repeat the string.
        
        Returns:
            String: The result of the repetition.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        """
        Checks if the string is considered true.
        
        Returns:
            bool: True if the string is non-empty, False otherwise.
        """
        return len(self.value) > 0

    def copy(self):
        """
        Creates a copy of the string.
        
        Returns:
            String: A new string instance with the same attributes.
        """
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        """
        Returns a string representation of the string.
        
        Returns:
            str: The string representation of the string.
        """
        return self.value

    def __repr__(self):
        """
        Returns a string representation of the string.
        
        Returns:
            str: The string representation of the string.
        """
        return f'"{self.value}"'

class List(Value):
    """
    Represents a list value in SpyLang.
    
    Attributes:
        elements (list): The elements in the list.
    """
    def __init__(self, elements):
        """
        Initializes a new list instance.
        
        Args:
            elements (list): The elements in the list.
        """
        super().__init__()
        self.elements = elements

    def added_to(self, other):
        """
        Adds an element to the list.
        
        Args:
            other (Value): The element to add.
        
        Returns:
            List: The updated list.
            Error: An error if the operation is not supported.
        """
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None

    def subbed_by(self, other):
        """
        Removes an element from the list by index.
        
        Args:
            other (Number): The index of the element to remove.
        
        Returns:
            List: The updated list.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Element at this index could not be removed from list because index is out of bounds',
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        """
        Concatenates the list with another list.
        
        Args:
            other (List): The other list to concatenate.
        
        Returns:
            List: The result of the concatenation.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        """
        Retrieves an element from the list by index.
        
        Args:
            other (Number): The index of the element to retrieve.
        
        Returns:
            Value: The retrieved element.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Element at this index could not be retrieved from list because index is out of bounds',
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)
    
    def copy(self):
        """
        Creates a copy of the list.
        
        Returns:
            List: A new list instance with the same attributes.
        """
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        """
        Returns a string representation of the list.
        
        Returns:
            str: The string representation of the list.
        """
        return ", ".join([str(x) for x in self.elements])
    
    def iterate(self):
        '''
        Returns an iterator for the list.
        
        Returns:
            Iterator: An iterator for the list.
        '''
        return iter(self.elements)

    def __repr__(self):
        """
        Returns a string representation of the list.
        
        Returns:
            str: The string representation of the list.
        """
        
        return f'[{", ".join([repr(x) for x in self.elements])}]'

#############################################################################
#  BASE FUNCTION
#################################################################################

class BaseFunction(Value):
    """
    Base class for all functions in SpyLang.
    
    Attributes:
        name (str): The name of the function.
    """
    def __init__(self, name):
        """
        Initializes a new base function instance.
        
        Args:
            name (str): The name of the function.
        """
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        """
        Generates a new context for the function.
        
        Returns:
            Context: The new context.
        """
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        """
        Checks if the correct number of arguments are passed to the function.
        
        Args:
            arg_names (list): The list of argument names.
            args (list): The list of arguments.
        
        Returns:
            RTResult: The result of checking the arguments.
        """
        res = RTResult()

        if len(args) > len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too many args passed into {self}",
                self.context
            ))
        
        if len(args) < len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)} too few args passed into {self}",
                self.context
            ))

        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        """
        Populates the function's context with the arguments.
        
        Args:
            arg_names (list): The list of argument names.
            args (list): The list of arguments.
            exec_ctx (Context): The execution context.
        """
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        """
        Checks and populates the function's context with the arguments.
        
        Args:
            arg_names (list): The list of argument names.
            args (list): The list of arguments.
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of checking and populating the arguments.
        """
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return(): return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)

########################################################################
# FUNTION CLASS
######################################################################

class Function(BaseFunction):
    """
    Represents a user-defined function in SpyLang.
    
    Attributes:
        body_node (Node): The node representing the body of the function.
        arg_names (list): The list of argument names.
        should_auto_return (bool): Whether the function should automatically return a value.
    """
    def __init__(self, name, body_node, arg_names, should_auto_return):
        """
        Initializes a new function instance.
        
        Args:
            name (str): The name of the function.
            body_node (Node): The node representing the body of the function.
            arg_names (list): The list of argument names.
            should_auto_return (bool): Whether the function should automatically return a value.
        """
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_auto_return = should_auto_return

    def execute(self, args):
        """
        Executes the function with the given arguments.
        
        Args:
            args (list): The list of arguments.
        
        Returns:
            RTResult: The result of executing the function.
        """
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return(): return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value == None: return res

        ret_value = (value if self.should_auto_return else None) or res.func_return_value or Number.null
        return res.success(ret_value)

    def copy(self):
        """
        Creates a copy of the function.
        
        Returns:
            Function: A new function instance with the same attributes.
        """
        copy = Function(self.name, self.body_node, self.arg_names, self.should_auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        """
        Returns a string representation of the function.
        
        Returns:
            str: The string representation of the function.
        """
        return f"<function {self.name}>"

####################################################################
# BUILTIN FUNCTIONS
#####################################################################

class BuiltInFunction(BaseFunction):
    """
    Represents a built-in function in SpyLang.
    """
    def __init__(self, name):
        """
        Initializes a new built-in function instance.
        
        Args:
            name (str): The name of the built-in function.
        """
        super().__init__(name)

    def execute(self, args):
        """
        Executes the built-in function with the given arguments.
        
        Args:
            args (list): The list of arguments.
        
        Returns:
            RTResult: The result of executing the built-in function.
        """
        res = RTResult()
        exec_ctx = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.should_return(): return res

        return_value = res.register(method(exec_ctx))
        if res.should_return(): return res
        return res.success(return_value)
    
    def no_visit_method(self, node, context):
        """
        Raises an exception if the built-in function method is not defined.
        
        Args:
            node (Node): The node being visited.
            context (Context): The context in which the node is being visited.
        
        Raises:
            Exception: If the built-in function method is not defined.
        """
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        """
        Creates a copy of the built-in function.
        
        Returns:
            BuiltInFunction: A new built-in function instance with the same attributes.
        """
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        """
        Returns a string representation of the built-in function.
        
        Returns:
            str: The string representation of the built-in function.
        """
        return f"<built-in function {self.name}>"

    #####################################

    def execute_print(self, exec_ctx):
        """
        Executes the 'print' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'print' function.
        """
        print(str(exec_ctx.symbol_table.get('value')))
        return RTResult().success('')
        
    execute_print.arg_names = ['value']
    
    def execute_print_ret(self, exec_ctx):
        """
        Executes the 'print_ret' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'print_ret' function.
        """
        return RTResult().success(String(str(exec_ctx.symbol_table.get('value'))))
    execute_print_ret.arg_names = ['value']
    
    def execute_input(self, exec_ctx):
        """
        Executes the 'input' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'input' function.
        """
        text = input()
        return RTResult().success(String(text))
    execute_input.arg_names = []

    def execute_input_int(self, exec_ctx):
        """
        Executes the 'input_int' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'input_int' function.
        """
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                return RTResult().success(Number(number))
    execute_input_int.arg_names = []

    def execute_clear(self, exec_ctx):
        """
        Executes the 'clear' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'clear' function.
        """
        os.system('cls' if os.name == 'nt' else 'cls') 
        return RTResult().success(Number.null)
    execute_clear.arg_names = []

    def execute_is_number(self, exec_ctx):
        """
        Executes the 'is_number' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'is_number' function.
        """
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, exec_ctx):
        """
        Executes the 'is_string' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'is_string' function.
        """
        is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, exec_ctx):
        """
        Executes the 'is_list' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'is_list' function.
        """
        is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, exec_ctx):
        """
        Executes the 'is_function' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'is_function' function.
        """
        is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_function.arg_names = ["value"]

    def execute_append(self, exec_ctx):
        """
        Executes the 'append' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'append' function.
        """
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        list_.elements.append(value)
        return RTResult().success(Number.null)
    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_ctx):
        """
        Executes the 'pop' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'pop' function.
        """
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(index, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be number",
                exec_ctx
            ))

        try:
            element = list_.elements.pop(index.value)
        except:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                'Element at this index could not be removed from list because index is out of bounds',
                exec_ctx
            ))
        return RTResult().success(element)
    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, exec_ctx):
        """
        Executes the 'extend' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'extend' function.
        """
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(listB, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be list",
                exec_ctx
            ))

        listA.elements.extend(listB.elements)
        return RTResult().success(Number.null)
    execute_extend.arg_names = ["listA", "listB"]

    def execute_len(self, exec_ctx):
        """
        Executes the 'len' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'len' function.
        """
        list_ = exec_ctx.symbol_table.get("list")

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be list",
                exec_ctx
            ))

        return RTResult().success(Number(len(list_.elements)))
    execute_len.arg_names = ["list"]

    def execute_run(self, exec_ctx):
        """
        Executes the 'run' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'run' function.
        """
        fn = exec_ctx.symbol_table.get("fn")

        if not isinstance(fn, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be string",
                exec_ctx
            ))

        fn = fn.value

        try:
            with open(fn, "r") as f:
                script = f.read().replace("\r\n", "\n")
        except Exception as e:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Failed to load script \"{fn}\"\n" + str(e),
                exec_ctx
            ))

        _, error = run(fn, script)
        
        if error:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Failed to finish executing script \"{fn}\"\n" +
                error.as_string(),
                exec_ctx
            ))

        return RTResult().success(Number.null)
    execute_run.arg_names = ["fn"]

BuiltInFunction.print       = BuiltInFunction("print")
BuiltInFunction.print_ret   = BuiltInFunction("print_ret")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.input_int   = BuiltInFunction("input_int")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.is_number   = BuiltInFunction("is_number")
BuiltInFunction.is_string   = BuiltInFunction("is_string")
BuiltInFunction.is_list     = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")
BuiltInFunction.len			= BuiltInFunction("len")
BuiltInFunction.run			= BuiltInFunction("run")

###############################################################
# CONTEXT
##################################################################

class Context:
    """
    Represents the context in which code is executed.
    
    Attributes:
        display_name (str): The name of the context.
        parent (Context): The parent context.
        parent_entry_pos (Position): The position in the source code where the context was entered.
        symbol_table (SymbolTable): The symbol table for the context.
    """
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        """
        Initializes a new context instance.
        
        Args:
            display_name (str): The name of the context.
            parent (Context): The parent context. Defaults to None.
            parent_entry_pos (Position): The position in the source code where the context was entered. Defaults to None.
        """
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

########################################################################
# SYMBOL TABLE
##############################################################################

class SymbolTable:
    """
    Represents a symbol table for storing variables and their values.
    
    Attributes:
        symbols (dict): A dictionary of symbols and their values.
        parent (SymbolTable): The parent symbol table.
    """
    def __init__(self, parent=None):
        """
        Initializes a new symbol table instance.
        
        Args:
            parent (SymbolTable): The parent symbol table. Defaults to None.
        """
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        """
        Retrieves the value of a symbol from the symbol table.
        
        Args:
            name (str): The name of the symbol.
        
        Returns:
            any: The value of the symbol, or None if the symbol is not found.
        """
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        """
        Sets the value of a symbol in the symbol table.
        
        Args:
            name (str): The name of the symbol.
            value (any): The value of the symbol.
        """
        self.symbols[name] = value

    def remove(self, name):
        """
        Removes a symbol from the symbol table.
        
        Args:
            name (str): The name of the symbol.
        """
        del self.symbols[name]

###############################################################################################
# INTERPRETER
#############################################################################################

class Interpreter:
    """
    The interpreter class is responsible for evaluating the abstract syntax tree (AST).
    """
    def visit(self, node, context):
        """
        Visits a node in the abstract syntax tree (AST) and evaluates it.
        
        Args:
            node (Node): The node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the node.
        
        Raises:
            Exception: If the visit method for the node type is not defined.
        """
        if isinstance(node, list):  
            raise Exception("Unexpected Python list object encountered during interpretation.")

        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        """
        Raises an exception if the visit method for the node type is not defined.
        
        Args:
            node (Node): The node being visited.
            context (Context): The context in which the node is being visited.
        
        Raises:
            Exception: If the visit method for the node type is not defined.
        """
        raise Exception(f'No visit_{type(node).__name__} method defined')

    ###################################

    def visit_NumberNode(self, node, context):
        """
        Visits a number node and evaluates it.
        
        Args:
            node (NumberNode): The number node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the number node.
        """
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_StringNode(self, node, context):
        """
        Visits a string node and evaluates it.
        
        Args:
            node (StringNode): The string node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the string node.
        """
        return RTResult().success(
            String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_RangeNode(self, node, context):
        """
        Visits a range node and evaluates it.
        
        Args:
            node (RangeNode): The range node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the range node.
        """
        res = RTResult()

        start_value = res.register(self.visit(node.start_node, context))
        if res.should_return(): return res

        end_value = res.register(self.visit(node.end_node, context))
        if res.should_return(): return res

        if not isinstance(start_value, Number) or not isinstance(end_value, Number):
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                "Range bounds must be numbers",
                context
            ))

        range_list = List([Number(i) for i in range(int(start_value.value), int(end_value.value) + 1)])
        return res.success(range_list)


    def visit_ListNode(self, node, context):
        """
        Visits a list node and evaluates it.
        
        Args:
            node (ListNode): The list node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the list node.
        """
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            element_value = res.register(self.visit(element_node, context))
            if res.should_return():
                return res
            elements.append(element_value)

        return res.success(List(elements))


    def visit_VarAccessNode(self, node, context):
        """
        Visits a variable access node and evaluates it.
        
        Args:
            node (VarAccessNode): The variable access node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the variable access node.
        """
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if value is None:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            ))

        if isinstance(value, int):
            value = Number(value)
        elif isinstance(value, float):
            value = Number(value)
        elif isinstance(value, str):
            value = String(value)
        elif isinstance(value, list):
            value = List(value)

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        """
        Visits a variable assignment node and evaluates it.
        
        Args:
            node (VarAssignNode): The variable assignment node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the variable assignment node.
        """
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.should_return(): return res

        if isinstance(value, list):
            value = List(value)

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        """
        Visits a binary operation node and evaluates it.
        
        Args:
            node (BinOpNode): The binary operation node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the binary operation node.
        """
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.should_return(): return res
        right = res.register(self.visit(node.right_node, context))
        if res.should_return(): return res

        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == TT_MOD:
            result, error = left.modded_by(right)
        elif node.op_tok.type == TT_POW:
            result, error = left.powed_by(right)
        elif node.op_tok.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TT_KEYWORD, 'and'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD, 'or'):
            result, error = left.ored_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        """
        Visits a unary operation node and evaluates it.
        
        Args:
            node (UnaryOpNode): The unary operation node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the unary operation node.
        """
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return(): return res

        error = None

        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_IfNode(self, node, context):
        """
        Visits an if statement node and evaluates it.
        
        Args:
            node (IfNode): The if statement node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the if statement node.
        """
        res = RTResult()

        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return(): return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return(): return res

                return res.success(Number.null if should_return_null else expr_value)

        if node.else_case:
            if isinstance(node.else_case, list):
                for expr in node.else_case:
                    res.register(self.visit(expr, context))
                    if res.should_return(): return res
                return res.success(Number.null)
            else:
              
                else_value = res.register(self.visit(node.else_case, context))
                if res.should_return(): return res
                return res.success(else_value)

        return res.success(Number.null)


    def visit_ForNode(self, node, context):
        """
        Visits a for loop node and evaluates it.
        
        Args:
            node (ForNode): The for loop node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the for loop node.
        """
        res = RTResult()
        elements = []

        iterable_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return():
            return res

        if isinstance(iterable_value, String):
            elements = iterable_value.value
        elif isinstance(iterable_value, List):
            elements = iterable_value.elements
        else:
            return res.failure(RTError(
                node.start_value_node.pos_start, node.start_value_node.pos_end,
                "Expected a string or a list to iterate over",
                context
            ))

        for element in elements:
            context.symbol_table.set(node.var_name_tok.value, element)
            body_result = res.register(self.visit(node.body_node, context))
            if res.should_return():
                if res.loop_should_continue:
                    continue
                if res.loop_should_break:
                    break
                return res  

        return res.success(None)




    def visit_WhileNode(self, node, context):
        """
        Visits a while loop node and evaluates it.
        
        Args:
            node (WhileNode): The while loop node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the while loop node.
        """
        res = RTResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return(): return res

            if not condition.is_true():
                break

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

            if res.loop_should_continue:
                continue
            
            if res.loop_should_break:
                break

            elements.append(value)

        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_FuncDefNode(self, node, context):
        """
        Visits a function definition node and evaluates it.
        
        Args:
            node (FuncDefNode): The function definition node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the function definition node.
        """
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)
        
        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        """
        Visits a function call node and evaluates it.
        
        Args:
            node (CallNode): The function call node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the function call node.
        """
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.should_return(): return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return(): return res

        return_value = res.register(value_to_call.execute(args))
        if res.should_return(): return res

        if isinstance(return_value, Value):
            return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)

        return res.success(return_value)

    def visit_ReturnNode(self, node, context):
        """
        Visits a return statement node and evaluates it.
        
        Args:
            node (ReturnNode): The return statement node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the return statement node.
        """
        res = RTResult()

        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return(): return res
        else:
            value = Number.null
        
        return res.success_return(value)

    def visit_ContinueNode(self, node, context):
        """
        Visits a continue statement node and evaluates it.
        
        Args:
            node (ContinueNode): The continue statement node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the continue statement node.
        """
        return RTResult().success_continue()

    def visit_BreakNode(self, node, context):
        """
        Visits a break statement node and evaluates it.
        
        Args:
            node (BreakNode): The break statement node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the break statement node.
        """
        return RTResult().success_break()

#######################################
# RUN
#######################################

Number.null = 0
Number.false = 0
Number.true = 1
Number.math_PI = math.pi

global_symbol_table = SymbolTable()
global_symbol_table.set("ghost", Number.null)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("true", Number.true)
global_symbol_table.set("math_pi", Number.math_PI)
global_symbol_table.set("transmit", BuiltInFunction.print)
global_symbol_table.set("transmit_ret", BuiltInFunction.print_ret)
global_symbol_table.set("intel", BuiltInFunction.input)
global_symbol_table.set("intel_int", BuiltInFunction.input_int)
global_symbol_table.set("erase", BuiltInFunction.clear)
global_symbol_table.set("is_code", BuiltInFunction.is_number)
global_symbol_table.set("is_msg", BuiltInFunction.is_string)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_mission", BuiltInFunction.is_function)
global_symbol_table.set("add_agent", BuiltInFunction.append)
global_symbol_table.set("withdraw", BuiltInFunction.pop)
global_symbol_table.set("expand", BuiltInFunction.extend)
global_symbol_table.set("length", BuiltInFunction.len)
global_symbol_table.set("launch", BuiltInFunction.run)

def run(fn, text):
    """
    Runs the SpyLang interpreter on the given source code.
    
    Args:
        fn (str): The filename of the source code.
        text (str): The source code text.
    
    Returns:
        any: The result of running the interpreter.
        Error: An error if one occurs during interpretation.
    """
    lexer = Lexer(fn, text)
    
    tokens, error = lexer.make_tokens()
    if error: return None, error
    
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    interpreter = Interpreter()
    context = Context("<program>")
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error



def run_file(filename):
    try:
        with open(filename, "r") as file:
            script = file.read()
        
        result, error = run(filename, script)
        if error:
            print(error.as_string())
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except KeyboardInterrupt:
        raise KeyboardInterruptError(details="Operation terminated by the user.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            Shell.shell()

        else:
            run_file(sys.argv[1])
            sys.exit(1)
    except KeyboardInterrupt:
        error = KeyboardInterruptError()
        print(error.as_string())
        sys.exit(1)

