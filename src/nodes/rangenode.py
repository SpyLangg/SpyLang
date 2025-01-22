from rtresult import RTResult
from values.number import Number
from errors import RTError
from values.rangevalue import RangeValue

class RangeNode:
    """
    Represents a range node in the abstract syntax tree (AST).

    Attributes:
        start_node (Node): The starting node of the range.
        end_node (Node): The ending node of the range.
        pos_start (Position): The starting position of the range in the source code.
        pos_end (Position): The ending position of the range in the source code.
    """
    def __init__(self, start_node, end_node):
        """
        Initializes a new range node instance.

        Args:
            start_node (Node): The starting node of the range.
            end_node (Node): The ending node of the range.
        """
        self.start_node = start_node
        self.end_node = end_node
        self.pos_start = self.start_node.pos_start
        self.pos_end = self.end_node.pos_end

    def evaluate(self, context):
        """
        Evaluate the range bounds and return a Range object.

        Args:
            context (Context): The runtime context.

        Returns:
            Range: The evaluated range.
        """
        res = RTResult()

 
        start_value = res.register(context.interpreter.visit(self.start_node, context))
        if res.should_return():
            return res


        end_value = res.register(context.interpreter.visit(self.end_node, context))
        if res.should_return():
            return res


        if not isinstance(start_value, Number) or not isinstance(end_value, Number):
            return res.failure(RTError(
                self.start_node.pos_start, self.end_node.pos_end,
                "Range bounds must be integers.",
                context
            ))

      
        start_int = int(start_value.value)
        end_int = int(end_value.value)
        return res.success(RangeValue(start_int, end_int))
