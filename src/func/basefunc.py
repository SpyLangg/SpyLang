from src.values.value import Value
from src.context import Context
from src.symboltable import SymbolTable
from src.rtresult import RTResult
from src.errors import RTError


class BaseFunction(Value):
    """
    Base class for all functions in SpyLang.
    
    Attributes:
        name (str): The name of the function.
    """
    def __init__(self, name):
        """
        Initializes a new base function instance.
        
        Args:
            name (str): The name of the function.
        """
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        """
        Generates a new context for the function.
        
        Returns:
            Context: The new context.
        """
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        """
        Checks if the correct number of arguments are passed to the function.
        
        Args:
            arg_names (list): The list of argument names.
            args (list): The list of arguments.
        
        Returns:
            RTResult: The result of checking the arguments.
        """
        res = RTResult()

        if len(args) > len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too many args passed into {self}",
                self.context
            ))
        
        if len(args) < len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)} too few args passed into {self}",
                self.context
            ))

        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        """
        Populates the function's context with the arguments.
        
        Args:
            arg_names (list): The list of argument names.
            args (list): The list of arguments.
            exec_ctx (Context): The execution context.
        """
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        """
        Checks and populates the function's context with the arguments.
        
        Args:
            arg_names (list): The list of argument names.
            args (list): The list of arguments.
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of checking and populating the arguments.
        """
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return(): return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)