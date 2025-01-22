

class Context:
    """
    Represents the context in which code is executed.
    
    Attributes:
        display_name (str): The name of the context.
        parent (Context): The parent context.
        parent_entry_pos (Position): The position in the source code where the context was entered.
        symbol_table (SymbolTable): The symbol table for the context.
    """
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        """
        Initializes a new context instance.
        
        Args:
            display_name (str): The name of the context.
            parent (Context): The parent context. Defaults to None.
            parent_entry_pos (Position): The position in the source code where the context was entered. Defaults to None.
        """
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None
