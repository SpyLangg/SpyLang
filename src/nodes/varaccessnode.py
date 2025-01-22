

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