

class ParseResult:
    """
    Represents the result of parsing a piece of source code.
    
    Attributes:
        error (Error): The error encountered during parsing, if any.
        node (Node): The root node of the parsed abstract syntax tree (AST).
        last_registered_advance_count (int): The number of tokens advanced during the last registered operation.
        advance_count (int): The total number of tokens advanced during parsing.
        to_reverse_count (int): The number of tokens to reverse if an error occurs.
    """
    def __init__(self):
        """
        Initializes a new parse result instance.
        """
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        """
        Registers an advancement in the token stream.
        """
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def register(self, res):
        """
        Registers a parse result.
        
        Args:
            res (ParseResult): The parse result to register.
        
        Returns:
            Node: The node from the registered parse result.
        """
        self.last_registered_advance_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node

    def try_register(self, res):
        """
        Tries to register a parse result, reversing the token stream if an error occurs.
        
        Args:
            res (ParseResult): The parse result to try to register.
        
        Returns:
            Node: The node from the registered parse result, or None if an error occurs.
        """
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def success(self, node):
        """
        Marks the parse result as successful.
        
        Args:
            node (Node): The root node of the parsed abstract syntax tree (AST).
        
        Returns:
            ParseResult: The updated parse result.
        """
        self.node = node
        return self

    def failure(self, error):
        """
        Marks the parse result as a failure.
        
        Args:
            error (Error): The error encountered during parsing.
        
        Returns:
            ParseResult: The updated parse result.
        """
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self