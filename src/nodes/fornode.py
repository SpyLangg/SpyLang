

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
        
