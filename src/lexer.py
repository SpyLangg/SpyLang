from src.constant import *
from src.position import Position
from src.tokens import Token
from src.errors import *

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
                    self.advance()
                    tokens.append(Token(TT_RANGE, pos_start=pos_start, pos_end=self.pos))
                else:
                    tokens.append(Token(TT_DOT, pos_start=self.pos))
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
            if self.current_char==None:
                break
            self.advance()
        self.advance()
