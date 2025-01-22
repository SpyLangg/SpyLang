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