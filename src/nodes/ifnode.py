
class IfNode:
    """
    Represents an if statement node in the abstract syntax tree (AST).
    
    Attributes:
        cases (list): A list of tuples representing the if and followup cases.
        else_case (list): A list of nodes representing the else case.
        pos_start (Position): The starting position of the if statement in the source code.
        pos_end (Position): The ending position of the if statement in the source code.
    """
    def __init__(self, cases, else_case=None):
        """
        Initializes a new if statement node instance.
        
        Args:
            cases (list): A list of tuples representing the if and followup cases.
            else_case (list): A list of nodes representing the else case. Defaults to an empty list.
        """
        self.cases = cases
        self.else_case = else_case or []  
        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (
            self.else_case[-1].pos_end if self.else_case and hasattr(self.else_case[-1], 'pos_end')
            else self.cases[-1][1].pos_end
        )
