class ListNode:
    """
    Represents a list node in the abstract syntax tree (AST).
    
    Attributes:
        element_nodes (list): A list of element nodes in the list.
        pos_start (Position): The starting position of the list in the source code.
        pos_end (Position): The ending position of the list in the source code.
    """
    def __init__(self, element_nodes, pos_start, pos_end):
        """
        Initializes a new list node instance.
        
        Args:
            element_nodes (list): A list of element nodes in the list.
            pos_start (Position): The starting position of the list.
            pos_end (Position): The ending position of the list.
        """
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end