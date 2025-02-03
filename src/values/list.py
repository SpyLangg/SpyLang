from src.values.value import Value
from src.values.number import Number
from src.errors import RTError


class List(Value):
    """
    Represents a list value in SpyLang.
    
    Attributes:
        elements (list): The elements in the list.
    """
    def __init__(self, elements):
        """
        Initializes a new list instance.
        
        Args:
            elements (list): The elements in the list.
        """
        super().__init__()
        self.elements = elements

    def added_to(self, other):
        """
        Adds an element to the list.
        
        Args:
            other (Value): The element to add.
        
        Returns:
            List: The updated list.
            Error: An error if the operation is not supported.
        """
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None

    def subbed_by(self, other):
        """
        Removes an element from the list by index.
        
        Args:
            other (Number): The index of the element to remove.
        
        Returns:
            List: The updated list.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Element at this index could not be removed from list because index is out of bounds',
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        """
        Concatenates the list with another list.
        
        Args:
            other (List): The other list to concatenate.
        
        Returns:
            List: The result of the concatenation.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        """
        Retrieves an element from the list by index.
        
        Args:
            other (Number): The index of the element to retrieve.
        
        Returns:
            Value: The retrieved element.
            Error: An error if the operation is not supported.
        """
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Element at this index could not be retrieved from list because index is out of bounds',
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)
    
    def copy(self):
        """
        Creates a copy of the list.
        
        Returns:
            List: A new list instance with the same attributes.
        """
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        """
        Returns a string representation of the list.
        
        Returns:
            str: The string representation of the list.
        """
        return ", ".join([str(x) for x in self.elements])
    
    def __iter__(self):
        '''
        Returns an iterator for the list.
        
        Returns:
            Iterator: An iterator for the list.
        '''
        return iter(self.elements)

    def __repr__(self):
        """
        Returns a string representation of the list.
        
        Returns:
            str: The string representation of the list.
        """
        
        return f"[" + ", ".join(repr(el) for el in self.elements) + "]"