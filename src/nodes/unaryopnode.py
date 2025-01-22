

class UnaryOpNode:
    """
    Represents a unary operation node in the abstract syntax tree (AST).
    
    Attributes:
        op_tok (Token): The token representing the operator.
        node (Node): The operand node.
        pos_start (Position): The starting position of the operation in the source code.
        pos_end (Position): The ending position of the operation in the source code.
    """
    def __init__(self, op_tok, node):
        """
        Initializes a new unary operation node instance.
        
        Args:
            op_tok (Token): The token representing the operator.
            node (Node): The operand node.
        """
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        """
        Returns a string representation of the unary operation node.
        
        Returns:
            str: A formatted string describing the unary operation node.
        """
        return f'({self.op_tok}, {self.node})'
