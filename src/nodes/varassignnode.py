

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
