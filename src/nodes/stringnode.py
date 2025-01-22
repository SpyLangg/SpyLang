
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
