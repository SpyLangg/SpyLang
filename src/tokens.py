

class Token:
    """
    Represents a single token in the SpyLang language, which can be an identifier, keyword, or operator.
    
    Attributes:
        type_ (str): The type of the token (e.g., INT, FLOAT, IDENTIFIER, KEYWORD).
        value (any): The value of the token (e.g., a number or string).
        pos_start (Position): The starting position of the token in the source code.
        pos_end (Position): The ending position of the token in the source code.
    """
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        """
        Initializes a new token instance.
        
        Args:
            type_ (str): The type of the token.
            value (any): The value of the token. Defaults to None.
            pos_start (Position): The starting position. Defaults to None.
            pos_end (Position): The ending position. Defaults to None.
        """
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, type_, value):
        """
        Checks if the token matches a given type and value.
        
        Args:
            type_ (str): The type to match.
            value (any): The value to match.
        
        Returns:
            bool: True if the token matches, False otherwise.
        """
        return self.type == type_ and self.value == value
    
    def __repr__(self):
        """
        Returns a string representation of the token.
        
        Returns:
            str: A formatted string describing the token.
        """
        if self.value:
            return f"Agent Report: {self.type} - Code: {self.value}"
        return f"Agent Status: {self.type} - No Value Assigned"
