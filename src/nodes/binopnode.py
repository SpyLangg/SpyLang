

class BinOpNode:
    """
    Represents a binary operation node in the abstract syntax tree (AST).
    
    Attributes:
        left_node (Node): The left operand node.
        op_tok (Token): The token representing the operator.
        right_node (Node): The right operand node.
        pos_start (Position): The starting position of the operation in the source code.
        pos_end (Position): The ending position of the operation in the source code.
    """
    def __init__(self, left_node, op_tok, right_node):
        """
        Initializes a new binary operation node instance.
        
        Args:
            left_node (Node): The left operand node.
            op_tok (Token): The token representing the operator.
            right_node (Node): The right operand node.
        """
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        """
        Returns a string representation of the binary operation node.
        
        Returns:
            str: A formatted string describing the binary operation node.
        """
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'