from strings_with_arrow import string_with_arrows

class Error:
    """
    Base class for all error types in SpyLang.
    
    Attributes:
        pos_start (Position): The starting position of the error in the source code.
        pos_end (Position): The ending position of the error in the source code.
        error_name (str): The name of the error.
        details (str): Additional details about the error.
    """
    def __init__(self, pos_start, pos_end, error_name, details):
        """
        Initializes a new error instance.
        
        Args:
            pos_start (Position): The starting position of the error.
            pos_end (Position): The ending position of the error.
            error_name (str): The name of the error.
            details (str): Additional details about the error.
        """
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        """
        Returns a string representation of the error.
        
        Returns:
            str: A formatted string describing the error.
        """
        result = f"{self.error_name}:{self.details}"
        result += f"File{self.pos_start.fn},line{self.pos_start.ln+1}"
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    """
    Error raised when an illegal character is encountered.
    """
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Agent Error: Unauthorized character detected in the operation. Mission compromised!", details)

class ExpectedCharError(Error):
    """
    Error raised when an expected character is not found.
    """
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Agent Error: Expected character not found in the operation. Mission compromised!", details)

class KeyboardInterruptError(Error):
    """
    Error raised when the user manually interrupts the program.
    """
    def __init__(self, pos_start=None, pos_end=None, details="The operation was manually aborted by the agent."):
        super().__init__(pos_start, pos_end, "Agent Error: Manual Termination Detected", details)


class InvalidSyntaxError(Error):
    """
    Error raised when invalid syntax is encountered.
    """
    def __init__(self, pos_start, pos_end, details=""):
        super().__init__(pos_start, pos_end, "Agent Error: Syntax anomaly encountered. The mission is incomplete.", details)

class RTError(Error):
    """
    Error raised during runtime.
    
    Attributes:
        context (Context): The context in which the error occurred.
    """
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, "Agent Error: Runtime breach! Unauthorized behavior detected in the system.", details)
        self.context = context

    def as_string(self):
        """
        Returns a string representation of the runtime error, including the traceback.
        
        Returns:
            str: A formatted string describing the error and its traceback.
        """
        result = self.generate_traceback()
        result += f"Agent Error: Mission failure detected. {self.error_name}: {self.details}. The operation cannot proceed."
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        """
        Generates a traceback for the error.
        
        Returns:
            str: A formatted string representing the traceback.
        """
        result = ""
        pos = self.pos_start
        ctx = self.context
        
        while ctx:
            result = f'Mission Log: File "{pos.fn}", line {str(pos.ln + 1)}, in {ctx.display_name}\n ' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        
        return 'Mission Traceback (Most Recent Incident Last):\n' + result

