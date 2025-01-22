from rtresult import RTResult
from values.number import Number
from values.list import List
from values.string import String
from values.rangevalue import RangeValue
from constant import *
from errors import RTError
from values.value import Value
from SpyLang import *
from func.basefunc import BaseFunction
# from function import Function

class Interpreter:
    """
    The interpreter class is responsible for evaluating the abstract syntax tree (AST).
    """
    def visit(self, node, context):
        """
        Visits a node in the abstract syntax tree (AST) and evaluates it.
        
        Args:
            node (Node): The node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the node.
        
        Raises:
            Exception: If the visit method for the node type is not defined.
        """
        if isinstance(node, list):  
            raise Exception("Unexpected Python list object encountered during interpretation.")

        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        """
        Raises an exception if the visit method for the node type is not defined.
        
        Args:
            node (Node): The node being visited.
            context (Context): The context in which the node is being visited.
        
        Raises:
            Exception: If the visit method for the node type is not defined.
        """
        raise Exception(f'No visit_{type(node).__name__} method defined')

    ###################################

    def visit_NumberNode(self, node, context):
        """
        Visits a number node and evaluates it.
        
        Args:
            node (NumberNode): The number node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the number node.
        """
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_StringNode(self, node, context):
        """
        Visits a string node and evaluates it.
        
        Args:
            node (StringNode): The string node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the string node.
        """
        return RTResult().success(
            String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    

    def visit_RangeNode(self, node, context):
        res = RTResult()

        start_value = res.register(self.visit(node.start_node, context))
        if res.should_return():
            return res

        end_value = res.register(self.visit(node.end_node, context))
        if res.should_return():
            return res

        if not isinstance(start_value, Number) or not isinstance(end_value, Number):
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                "Range bounds must be integers.",
                context
            ))

        start = int(start_value.value)
        end = int(end_value.value)
        return res.success(RangeValue(start, end))


    def visit_ListNode(self, node, context):
        """
        Visits a list node and evaluates it.
        
        Args:
            node (ListNode): The list node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the list node.
        """
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            element_value = res.register(self.visit(element_node, context))
            if res.should_return():
                return res
            elements.append(element_value)

        return res.success(List(elements))


    def visit_VarAccessNode(self, node, context):
        """
        Visits a variable access node and evaluates it.
        
        Args:
            node (VarAccessNode): The variable access node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the variable access node.
        """
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if value is None:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            ))

        if isinstance(value, int):
            value = Number(value)
        elif isinstance(value, float):
            value = Number(value)
        elif isinstance(value, str):
            value = String(value)
        elif isinstance(value, list):
            value = List(value)

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        """
        Visits a variable assignment node and evaluates it.
        
        Args:
            node (VarAssignNode): The variable assignment node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the variable assignment node.
        """
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.should_return(): return res

        if isinstance(value, list):
            value = List(value)

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        """
        Visits a binary operation node and evaluates it.
        
        Args:
            node (BinOpNode): The binary operation node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the binary operation node.
        """
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.should_return(): return res
        right = res.register(self.visit(node.right_node, context))
        if res.should_return(): return res

        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == TT_MOD:
            result, error = left.modded_by(right)
        elif node.op_tok.type == TT_POW:
            result, error = left.powed_by(right)
        elif node.op_tok.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TT_KEYWORD, 'and'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD, 'or'):
            result, error = left.ored_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        """
        Visits a unary operation node and evaluates it.
        
        Args:
            node (UnaryOpNode): The unary operation node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the unary operation node.
        """
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return(): return res

        error = None

        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_IfNode(self, node, context):
        """
        Visits an if statement node and evaluates it.
        
        Args:
            node (IfNode): The if statement node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the if statement node.
        """
        res = RTResult()

        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return(): return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return(): return res

                return res.success(Number.null if should_return_null else expr_value)

        if node.else_case:
            if isinstance(node.else_case, list):
                for expr in node.else_case:
                    res.register(self.visit(expr, context))
                    if res.should_return(): return res
                return res.success(Number.null)
            else:
              
                else_value = res.register(self.visit(node.else_case, context))
                if res.should_return(): return res
                return res.success(else_value)

        return res.success(Number.null)



    def visit_ForNode(self, node, context):
        """
        Execute a 'for' loop node in the runtime context.

        Args:
            node (ForNode): The 'for' loop node to execute.
            context (Context): The runtime context.

        Returns:
            RTResult: The result of executing the 'for' loop.
        """
        res = RTResult()

        iterable_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return():
            return res

        if isinstance(iterable_value, RangeValue):
            elements = list(iterable_value.iter())
        elif isinstance(iterable_value, List):
            elements = iterable_value.elements
        elif isinstance(iterable_value, String):
            elements = list(iterable_value.value)
        else:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                "Expected a list, string, or range as an iterable.",
                context
            ))

        
        for element in elements:
            context.symbol_table.set(node.var_name_tok.value, element)
            result = res.register(self.visit(node.body_node, context))
            if res.should_return() and not res.loop_should_continue and not res.loop_should_break:
                return res

            if res.loop_should_continue:
                continue
            if res.loop_should_break:
                break

        return res.success(None)

    
    def visit_WhileNode(self, node, context):
        """
        Visits a while loop node and evaluates it.
        
        Args:
            node (WhileNode): The while loop node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the while loop node.
        """
        res = RTResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return(): return res

            if not condition.is_true():
                break

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

            if res.loop_should_continue:
                continue
            
            if res.loop_should_break:
                break

            elements.append(value)

        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_FuncDefNode(self, node, context):
        """
        Visits a function definition node and evaluates it.
        
        Args:
            node (FuncDefNode): The function definition node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the function definition node.
        """
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)
        
        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        """
        Visits a function call node and evaluates it.
        
        Args:
            node (CallNode): The function call node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the function call node.
        """
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.should_return(): return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return(): return res

        return_value = res.register(value_to_call.execute(args))
        if res.should_return(): return res

        if isinstance(return_value, Value):
            return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)

        return res.success(return_value)

    def visit_ReturnNode(self, node, context):
        """
        Visits a return statement node and evaluates it.
        
        Args:
            node (ReturnNode): The return statement node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the return statement node.
        """
        res = RTResult()

        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return(): return res
        else:
            value = Number.null
        
        return res.success_return(value)

    def visit_ContinueNode(self, node, context):
        """
        Visits a continue statement node and evaluates it.
        
        Args:
            node (ContinueNode): The continue statement node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the continue statement node.
        """
        return RTResult().success_continue()

    def visit_BreakNode(self, node, context):
        """
        Visits a break statement node and evaluates it.
        
        Args:
            node (BreakNode): The break statement node to visit.
            context (Context): The context in which the node is being evaluated.
        
        Returns:
            RTResult: The result of evaluating the break statement node.
        """
        return RTResult().success_break()



class Function(BaseFunction):
    """
    Represents a user-defined function in SpyLang.
    
    Attributes:
        body_node (Node): The node representing the body of the function.
        arg_names (list): The list of argument names.
        should_auto_return (bool): Whether the function should automatically return a value.
    """
    def __init__(self, name, body_node, arg_names, should_auto_return):
        """
        Initializes a new function instance.
        
        Args:
            name (str): The name of the function.
            body_node (Node): The node representing the body of the function.
            arg_names (list): The list of argument names.
            should_auto_return (bool): Whether the function should automatically return a value.
        """
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_auto_return = should_auto_return

    def execute(self, args):
        """
        Executes the function with the given arguments.
        
        Args:
            args (list): The list of arguments.
        
        Returns:
            RTResult: The result of executing the function.
        """
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return(): return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value == None: return res

        ret_value = (value if self.should_auto_return else None) or res.func_return_value or Number.null
        return res.success(ret_value)

    def copy(self):
        """
        Creates a copy of the function.
        
        Returns:
            Function: A new function instance with the same attributes.
        """
        copy = Function(self.name, self.body_node, self.arg_names, self.should_auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        """
        Returns a string representation of the function.
        
        Returns:
            str: The string representation of the function.
        """
        return f"<function {self.name}>"