

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
