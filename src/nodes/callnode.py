class CallNode:
    """
    Represents a function call node in the abstract syntax tree (AST).
    
    Attributes:
        node_to_call (Node): The node representing the function to be called.
        arg_nodes (list): A list of nodes representing the function arguments.
        pos_start (Position): The starting position of the function call in the source code.
        pos_end (Position): The ending position of the function call in the source code.
    """
    def __init__(self, node_to_call, arg_nodes):
        """
        Initializes a new function call node instance.
        
        Args:
            node_to_call (Node): The node representing the function to be called.
            arg_nodes (list): A list of nodes representing the function arguments.
        """
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes
        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end