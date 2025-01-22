from errors import RTError
from rtresult import RTResult

class Value:
    """
    Base class for all values in SpyLang.
    
    Attributes:
        pos_start (Position): The starting position of the value in the source code.
        pos_end (Position): The ending position of the value in the source code.
        context (Context): The context in which the value exists.
    """
    def __init__(self):
        """
        Initializes a new value instance.
        """
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        """
        Sets the position of the value in the source code.
        
        Args:
            pos_start (Position): The starting position. Defaults to None.
            pos_end (Position): The ending position. Defaults to None.
        
        Returns:
            Value: The updated value instance.
        """
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        """
        Sets the context of the value.
        
        Args:
            context (Context): The context in which the value exists. Defaults to None.
        
        Returns:
            Value: The updated value instance.
        """
        self.context = context
        return self

    def added_to(self, other):
        """
        Adds the value to another value.
        
        Args:
            other (Value): The other value to add.
        
        Returns:
            Value: The result of the addition.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        """
        Subtracts another value from the value.
        
        Args:
            other (Value): The other value to subtract.
        
        Returns:
            Value: The result of the subtraction.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        """
        Multiplies the value by another value.
        
        Args:
            other (Value): The other value to multiply.
        
        Returns:
            Value: The result of the multiplication.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        """
        Divides the value by another value.
        
        Args:
            other (Value): The other value to divide.
        
        Returns:
            Value: The result of the division.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        """
        Raises the value to the power of another value.
        
        Args:
            other (Value): The other value to use as the exponent.
        
        Returns:
            Value: The result of the exponentiation.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        """
        Compares the value for equality with another value.
        
        Args:
            other (Value): The other value to compare.
        
        Returns:
            Value: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        """
        Compares the value for inequality with another value.
        
        Args:
            other (Value): The other value to compare.
        
        Returns:
            Value: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        """
        Compares the value for less-than with another value.
        
        Args:
            other (Value): The other value to compare.
        
        Returns:
            Value: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        """
        Compares the value for greater-than with another value.
        
        Args:
            other (Value): The other value to compare.
        
        Returns:
            Value: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        """
        Compares the value for less-than-or-equal-to with another value.
        
        Args:
            other (Value): The other value to compare.
        
        Returns:
            Value: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        """
        Compares the value for greater-than-or-equal-to with another value.
        
        Args:
            other (Value): The other value to compare.
        
        Returns:
            Value: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        """
        Performs a logical AND operation with another value.
        
        Args:
            other (Value): The other value to AND with.
        
        Returns:
            Value: The result of the AND operation.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        """
        Performs a logical OR operation with another value.
        
        Args:
            other (Value): The other value to OR with.
        
        Returns:
            Value: The result of the OR operation.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def notted(self, other):
        """
        Performs a logical NOT operation on the value.
        
        Args:
            other (Value): The other value to NOT.
        
        Returns:
            Value: The result of the NOT operation.
            Error: An error if the operation is not supported.
        """
        return None, self.illegal_operation(other)

    def execute(self, args):
        """
        Executes the value as a function.
        
        Args:
            args (list): The arguments to pass to the function.
        
        Returns:
            RTResult: The result of executing the function.
        """
        return RTResult().failure(self.illegal_operation())

    def copy(self):
        """
        Creates a copy of the value.
        
        Returns:
            Value: A new value instance with the same attributes.
        """
        raise Exception('No copy method defined')

    def is_true(self):
        """
        Checks if the value is considered true.
        
        Returns:
            bool: True if the value is considered true, False otherwise.
        """
        return False

    def illegal_operation(self, other=None):
        """
        Creates an illegal operation error.
        
        Args:
            other (Value): The other value involved in the operation. Defaults to None.
        
        Returns:
            RTError: The illegal operation error.
        """
        if not other: other = self
        return RTError(
            self.pos_start, other.pos_end,
            'Illegal operation',
            self.context
        )
