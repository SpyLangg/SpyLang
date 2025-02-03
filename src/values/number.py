from src.values.value import Value
from src.errors import RTError

class Number(Value):
    """
    Represents a number value in SpyLang.
    
    Attributes:
        value (float): The numeric value.
    """
    def __init__(self, value):
        """
        Initializes a new number instance.
        
        Args:
            value (float): The numeric value.
        """
        super().__init__()
        self.value = value

    def to_int(self):
        if isinstance(self.value, Number): 
            return int(self.value.value)
        return int(self.value)


    def added_to(self, other):
        """
        Adds the number to another number.
        
        Args:
            other (Number): The other number to add.
        
        Returns:
            Number: The result of the addition.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(self.to_int() + other.value).set_context(self.context), None
        elif isinstance(other, int):
            return Number(self.value + other).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)



    def subbed_by(self, other):
        """
        Subtracts another number from the number.
        
        Args:
            other (Number): The other number to subtract.
        
        Returns:
            Number: The result of the subtraction.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        elif isinstance(other, (int, float)):
            return Number(self.value - other).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        """
        Multiplies the number by another number.
        
        Args:
            other (Number): The other number to multiply.
        
        Returns:
            Number: The result of the multiplication.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        elif isinstance(other, (int, float)):
            return Number(self.value * other).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        """
        Divides the number by another number.
        
        Args:
            other (Number): The other number to divide.
        
        Returns:
            Number: The result of the division.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )
        elif isinstance(other, (int, float)):
            if other == 0:
                return None, RTError(
                    self.pos_start, self.pos_end,
                    "Division by zero"
                )

            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
    def modded_by(self, other):
        """
        Modulus the number by another number.
        
        Args:
            other (Number): The other number to modulus.
        
        Returns:
            Number: The result of the modulus.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Number(self.value % other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        """
        Raises the number to the power of another number.
        
        Args:
            other (Number): The other number to use as the exponent.
        
        Returns:
            Number: The result of the exponentiation.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        """
        Compares the number for equality with another number.
        
        Args:
            other (Number): The other number to compare.
        
        Returns:
            Number: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        """
        Compares the number for inequality with another number.
        
        Args:
            other (Number): The other number to compare.
        
        Returns:
            Number: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        """
        Compares the number for less-than with another number.
        
        Args:
            other (Number): The other number to compare.
        
        Returns:
            Number: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        """
        Compares the number for greater-than with another number.
        
        Args:
            other (Number): The other number to compare.
        
        Returns:
            Number: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        """
        Compares the number for less-than-or-equal-to with another number.
        
        Args:
            other (Number): The other number to compare.
        
        Returns:
            Number: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        """
        Compares the number for greater-than-or-equal-to with another number.
        
        Args:
            other (Number): The other number to compare.
        
        Returns:
            Number: The result of the comparison.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        """
        Performs a logical AND operation with another number.
        
        Args:
            other (Number): The other number to AND with.
        
        Returns:
            Number: The result of the AND operation.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        """
        Performs a logical OR operation with another number.
        
        Args:
            other (Number): The other number to OR with.
        
        Returns:
            Number: The result of the OR operation.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        """
        Performs a logical NOT operation on the number.
        
        Returns:
            Number: The result of the NOT operation.
            Error: An error if the operation is not supported.
        """
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        """
        Creates a copy of the number.
        
        Returns:
            Number: A new number instance with the same attributes.
        """
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        """
        Checks if the number is considered true.
        
        Returns:
            bool: True if the number is non-zero, False otherwise.
        """
        return self.value != 0

    def __str__(self):
        """
        Returns a string representation of the number.
        
        Returns:
            str: The string representation of the number.
        """
        return str(self.value)
    
    def __repr__(self):
        """
        Returns a string representation of the number.
        
        Returns:
            str: The string representation of the number.
        """
        return str(self.value)