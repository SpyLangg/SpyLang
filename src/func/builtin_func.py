from func.basefunc import BaseFunction
from rtresult import RTResult
from values.string import String
import os
from values.number import Number
from values.list import List
from errors import RTError
from symboltable import SymbolTable
from lexer import Lexer
from parser import Parser
from interpreterr import Interpreter
from context import Context


class BuiltInFunction(BaseFunction):
    """
    Represents a built-in function in SpyLang.
    """
    def __init__(self, name):
        """
        Initializes a new built-in function instance.
        
        Args:
            name (str): The name of the built-in function.
        """
        super().__init__(name)

    def execute(self, args):
        """
        Executes the built-in function with the given arguments.
        
        Args:
            args (list): The list of arguments.
        
        Returns:
            RTResult: The result of executing the built-in function.
        """
        res = RTResult()
        exec_ctx = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.should_return(): return res

        return_value = res.register(method(exec_ctx))
        if res.should_return(): return res
        return res.success(return_value)
    
    def no_visit_method(self, node, context):
        """
        Raises an exception if the built-in function method is not defined.
        
        Args:
            node (Node): The node being visited.
            context (Context): The context in which the node is being visited.
        
        Raises:
            Exception: If the built-in function method is not defined.
        """
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        """
        Creates a copy of the built-in function.
        
        Returns:
            BuiltInFunction: A new built-in function instance with the same attributes.
        """
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        """
        Returns a string representation of the built-in function.
        
        Returns:
            str: The string representation of the built-in function.
        """
        return f"<built-in function {self.name}>"

    #####################################

    def execute_print(self, exec_ctx):
        """
        Executes the 'print' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'print' function.
        """
        print(str(exec_ctx.symbol_table.get('value')))
        return RTResult().success('')
        
    execute_print.arg_names = ['value']
    
    def execute_print_ret(self, exec_ctx):
        """
        Executes the 'print_ret' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'print_ret' function.
        """
        return RTResult().success(String(str(exec_ctx.symbol_table.get('value'))))
    execute_print_ret.arg_names = ['value']
    
    def execute_input(self, exec_ctx):
        """
        Executes the 'input' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'input' function.
        """
        text = input()
        return RTResult().success(String(text))
    execute_input.arg_names = []

    def execute_input_int(self, exec_ctx):
        """
        Executes the 'input_int' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'input_int' function.
        """
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                return RTResult().success(Number(number))
    execute_input_int.arg_names = []

    def execute_clear(self, exec_ctx):
        """
        Executes the 'clear' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'clear' function.
        """
        os.system('cls' if os.name == 'nt' else 'cls') 
        return RTResult().success(Number.null)
    execute_clear.arg_names = []

    def execute_is_number(self, exec_ctx):
        """
        Executes the 'is_number' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'is_number' function.
        """
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, exec_ctx):
        """
        Executes the 'is_string' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'is_string' function.
        """
        is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, exec_ctx):
        """
        Executes the 'is_list' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'is_list' function.
        """
        is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, exec_ctx):
        """
        Executes the 'is_function' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'is_function' function.
        """
        is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_function.arg_names = ["value"]

    def execute_append(self, exec_ctx):
        """
        Executes the 'append' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'append' function.
        """
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        list_.elements.append(value)
        return RTResult().success(Number.null)
    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_ctx):
        """
        Executes the 'pop' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'pop' function.
        """
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(index, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be number",
                exec_ctx
            ))

        try:
            element = list_.elements.pop(index.value)
        except:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                'Element at this index could not be removed from list because index is out of bounds',
                exec_ctx
            ))
        return RTResult().success(element)
    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, exec_ctx):
        """
        Executes the 'extend' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'extend' function.
        """
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(listB, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be list",
                exec_ctx
            ))

        listA.elements.extend(listB.elements)
        return RTResult().success(Number.null)
    execute_extend.arg_names = ["listA", "listB"]

    def execute_len(self, exec_ctx):
        """
        Executes the 'len' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'len' function.
        """
        list_ = exec_ctx.symbol_table.get("list")

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be list",
                exec_ctx
            ))

        return RTResult().success(Number(len(list_.elements)))
    execute_len.arg_names = ["list"]

    def execute_run(self, exec_ctx):
        """
        Executes the 'run' built-in function.
        
        Args:
            exec_ctx (Context): The execution context.
        
        Returns:
            RTResult: The result of executing the 'run' function.
        """
        fn = exec_ctx.symbol_table.get("fn")

        if not isinstance(fn, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be string",
                exec_ctx
            ))

        fn = fn.value

        try:
            with open(fn, "r") as f:
                script = f.read().replace("\r\n", "\n")
        except Exception as e:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Failed to load script \"{fn}\"\n" + str(e),
                exec_ctx
            ))

        _, error = run(fn, script)
        
        if error:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Failed to finish executing script \"{fn}\"\n" +
                error.as_string(),
                exec_ctx
            ))

        return RTResult().success(Number.null)
    execute_run.arg_names = ["fn"]

BuiltInFunction.print       = BuiltInFunction("print")
BuiltInFunction.print_ret   = BuiltInFunction("print_ret")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.input_int   = BuiltInFunction("input_int")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.is_number   = BuiltInFunction("is_number")
BuiltInFunction.is_string   = BuiltInFunction("is_string")
BuiltInFunction.is_list     = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")
BuiltInFunction.len			= BuiltInFunction("len")
BuiltInFunction.run			= BuiltInFunction("run")


import math

Number.null = 0
Number.false = 0
Number.true = 1
Number.math_PI = math.pi

global_symbol_table = SymbolTable()
global_symbol_table.set("ghost", Number.null)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("true", Number.true)
global_symbol_table.set("math_pi", Number.math_PI)
global_symbol_table.set("transmit", BuiltInFunction.print)
global_symbol_table.set("transmit_ret", BuiltInFunction.print_ret)
global_symbol_table.set("intel", BuiltInFunction.input)
global_symbol_table.set("intel_int", BuiltInFunction.input_int)
global_symbol_table.set("erase", BuiltInFunction.clear)
global_symbol_table.set("is_code", BuiltInFunction.is_number)
global_symbol_table.set("is_msg", BuiltInFunction.is_string)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_mission", BuiltInFunction.is_function)
global_symbol_table.set("add_agent", BuiltInFunction.append)
global_symbol_table.set("withdraw", BuiltInFunction.pop)
global_symbol_table.set("expand", BuiltInFunction.extend)
global_symbol_table.set("length", BuiltInFunction.len)
global_symbol_table.set("launch", BuiltInFunction.run)


def run(fn, text):
    """
    Runs the SpyLang interpreter on the given source code.
    
    Args:
        fn (str): The filename of the source code.
        text (str): The source code text.
    
    Returns:
        any: The result of running the interpreter.
        Error: An error if one occurs during interpretation.
    """
    lexer = Lexer(fn, text)
    
    tokens, error = lexer.make_tokens()
    if error: return None, error
    
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    interpreter = Interpreter()
    context = Context("<program>")
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error