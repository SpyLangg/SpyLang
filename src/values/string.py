from src.values.value import Value
from src.values.number import Number

class String(Value):
    """
    Represents a string value in SpyLang.
    
    Attributes:
        value (str): The string value.
    """
    def __init__(self, value):
        """
        Initializes a new string instance.
        
        Args:
            value (str): The string value.
        """
        super().__init__()
        self.value = value

    def added_to(self, other):
        """
        Concatenates the string with another string.
        
        Args:
            other (String): The other string to concatenate.
        
        Returns:
            String: The result of the concatenation.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        """
        Repeats the string a specified number of times.
        
        Args:
            other (Number): The number of times to repeat the string.
        
        Returns:
            String: The result of the repetition.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        """
        Checks if the string is considered true.
        
        Returns:
            bool: True if the string is non-empty, False otherwise.
        """
        return len(self.value) > 0

    def copy(self):
        """
        Creates a copy of the string.
        
        Returns:
            String: A new string instance with the same attributes.
        """
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        """
        Returns a string representation of the string.
        
        Returns:
            str: The string representation of the string.
        """
        return self.value

    def __repr__(self):
        """
        Returns a string representation of the string.
        
        Returns:
            str: The string representation of the string.
        """
        return f'"{self.value}"'


