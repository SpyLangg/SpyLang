

class RTResult:
    """
    Represents the result of evaluating a node during interpretation.
    
    Attributes:
        value (any): The value resulting from the evaluation.
        error (Error): The error encountered during evaluation, if any.
        func_return_value (any): The value to return from a function, if any.
        loop_should_continue (bool): Whether a loop should continue.
        loop_should_break (bool): Whether a loop should break.
    """
    def __init__(self):
        """
        Initializes a new runtime result instance.
        """
        self.reset()

    def reset(self):
        """
        Resets the runtime result to its initial state.
        """
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, res):
        """
        Registers a runtime result.
        
        Args:
            res (RTResult): The runtime result to register.
        
        Returns:
            any: The value from the registered runtime result.
        """
        self.error = res.error
        self.func_return_value = res.func_return_value
        self.loop_should_continue = res.loop_should_continue
        self.loop_should_break = res.loop_should_break
        return res.value

    def success(self, value):
        """
        Marks the runtime result as successful.
        
        Args:
            value (any): The value resulting from the evaluation.
        
        Returns:
            RTResult: The updated runtime result.
        """
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        """
        Marks the runtime result as a successful function return.
        
        Args:
            value (any): The value to return from the function.
        
        Returns:
            RTResult: The updated runtime result.
        """
        self.reset()
        self.func_return_value = value
        return self
    
    def success_continue(self):
        """
        Marks the runtime result as a successful loop continuation.
        
        Returns:
            RTResult: The updated runtime result.
        """
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        """
        Marks the runtime result as a successful loop break.
        
        Returns:
            RTResult: The updated runtime result.
        """
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        """
        Marks the runtime result as a failure.
        
        Args:
            error (Error): The error encountered during evaluation.
        
        Returns:
            RTResult: The updated runtime result.
        """
        self.reset()
        self.error = error
        return self

    def should_return(self):
        """
        Checks if the runtime result should return (due to an error, function return, loop continuation, or loop break).
        
        Returns:
            bool: True if the runtime result should return, False otherwise.
        """
        return (
            self.error or
            self.func_return_value or
            self.loop_should_continue or
            self.loop_should_break
        )
