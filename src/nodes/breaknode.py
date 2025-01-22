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