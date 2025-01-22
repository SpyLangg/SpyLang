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