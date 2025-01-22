

class FuncDefNode:
    """
    Represents a function definition node in the abstract syntax tree (AST).
    
    Attributes:
        var_name_tok (Token): The token representing the function name.
        arg_name_toks (list): A list of tokens representing the function arguments.
        body_node (Node): The node representing the body of the function.
        should_auto_return (bool): Whether the function should automatically return a value.
        pos_start (Position): The starting position of the function definition in the source code.
        pos_end (Position): The ending position of the function definition in the source code.
    """
    def __init__(self, var_name_tok, arg_name_toks, body_node, should_auto_return):
        """
        Initializes a new function definition node instance.
        
        Args:
            var_name_tok (Token): The token representing the function name.
            arg_name_toks (list): A list of tokens representing the function arguments.
            body_node (Node): The node representing the body of the function.
            should_auto_return (bool): Whether the function should automatically return a value.
        """
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.should_auto_return = should_auto_return

        if self.var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end
