

class SymbolTable:
    """
    Represents a symbol table for storing variables and their values.
    
    Attributes:
        symbols (dict): A dictionary of symbols and their values.
        parent (SymbolTable): The parent symbol table.
    """
    def __init__(self, parent=None):
        """
        Initializes a new symbol table instance.
        
        Args:
            parent (SymbolTable): The parent symbol table. Defaults to None.
        """
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        """
        Retrieves the value of a symbol from the symbol table.
        
        Args:
            name (str): The name of the symbol.
        
        Returns:
            any: The value of the symbol, or None if the symbol is not found.
        """
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        """
        Sets the value of a symbol in the symbol table.
        
        Args:
            name (str): The name of the symbol.
            value (any): The value of the symbol.
        """
        self.symbols[name] = value

    def remove(self, name):
        """
        Removes a symbol from the symbol table.
        
        Args:
            name (str): The name of the symbol.
        """
        del self.symbols[name]