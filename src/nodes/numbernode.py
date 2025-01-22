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