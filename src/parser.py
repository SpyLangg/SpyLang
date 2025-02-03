from src.constant import *
from src.errors import *
from src.parseresult import ParseResult
from src.nodes.numbernode import NumberNode
from src.nodes.stringnode import StringNode
from src.nodes.listnode import ListNode
from src.nodes.varaccessnode import VarAccessNode
from src.nodes.rangenode import RangeNode
from src.nodes.varassignnode import VarAssignNode
from src.nodes.binopnode import BinOpNode
from src.nodes.unaryopnode import UnaryOpNode
from src.nodes.ifnode import IfNode
from src.nodes.whilenode import WhileNode
from src.nodes.fornode import ForNode
from src.nodes.funcdefnode import FuncDefNode
from src.nodes.returnnode import ReturnNode
from src.nodes.callnode import CallNode
from src.nodes.continuenode import ContinueNode
from src.nodes.breaknode import BreakNode

class Parser:
    """
    The parser class is responsible for converting a list of tokens into an abstract syntax tree (AST).
    
    Attributes:
        tokens (list): The list of tokens to parse.
        tok_idx (int): The current index in the token list.
        current_tok (Token): The current token being processed.
    """
    def __init__(self, tokens):
        """
        Initializes a new parser instance.
        
        Args:
            tokens (list): The list of tokens to parse.
        """
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        """
        Advances to the next token in the token list.
        
        Returns:
            Token: The updated current token.
        """
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        """
        Reverses the token stream by a specified amount.
        
        Args:
            amount (int): The number of tokens to reverse. Defaults to 1.
        
        Returns:
            Token: The updated current token.
        """
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        """
        Updates the current token based on the current index in the token list.
        """
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]


    def range_expr(self):
        """
        Parses a range expression from the token list.

        Returns:
            ParseResult: The result of parsing the range expression.
        """
        res = ParseResult()

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()

        start_value = res.register(self.arith_expr())
        if res.error:
            return res

        if self.current_tok.type != TT_RANGE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '..' for range"
            ))

        res.register_advancement()
        self.advance()


        end_value = res.register(self.arith_expr())
        if res.error:
            return res

        if self.current_tok.type == TT_RPAREN:
            res.register_advancement()
            self.advance()

        return res.success(RangeNode(start_value, end_value))
    

    def parse(self):
        """
        Parses the token list into an abstract syntax tree (AST).
        
        Returns:
            ParseResult: The result of parsing the token list.
        """
        res = self.statements()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Unexpected token: {self.current_tok}"
            ))
        return res

    ###################################

    def statements(self):
        """
        Parses a series of statements from the token list.
        
        Returns:
            ParseResult: The result of parsing the statements.
        """
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        while self.current_tok.type == TT_NEWLINE:
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                break
            statements.append(statement)

        return res.success(ListNode(statements, pos_start, self.current_tok.pos_end.copy()))

    def statement(self):
        """
        Parses a single statement from the token list.
        
        Returns:
            ParseResult: The result of parsing the statement.
        """
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.matches(TT_KEYWORD, 'extract'):
            res.register_advancement()
            self.advance()

            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))
        
        if self.current_tok.matches(TT_KEYWORD, 'proceed'):
            res.register_advancement()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))
            
        if self.current_tok.matches(TT_KEYWORD, 'abort'):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

        expr = res.register(self.expr())
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'extract', 'proceed', 'abort', 'assign', 'check', 'each', 'chase', 'mission', int, float, identifier, '+', '-', '(', '[' or 'not'"
            ))
        return res.success(expr)

    def expr(self):
        """
        Parses an expression from the token list.
        
        Returns:
            ParseResult: The result of parsing the expression.
        """
        res = ParseResult()


        if self.current_tok.matches(TT_KEYWORD, 'assign'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier after 'assign'"
                ))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '=' after variable name"
                ))

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res

            return res.success(VarAssignNode(var_name, expr))

      
        if self.current_tok.type == TT_IDENTIFIER:
            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TT_EQ:
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                if res.error:
                    return res
                return res.success(VarAssignNode(var_name, expr))

            
            self.reverse()

      
        node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'assign', 'check', 'each', 'chase', 'mission', int, float, identifier, '+', '-', '(', '[' or 'not'"
            ))

        return res.success(node)

    def comp_expr(self):
        """
        Parses a comparison expression from the token list.
        
        Returns:
            ParseResult: The result of parsing the comparison expression.
        """
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'not'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))
        
        node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))
        
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected int, float, identifier, '+', '-', '(', '[', 'check', 'each', 'chase', 'mission' or 'not'"
            ))

        return res.success(node)

    def arith_expr(self):
        """
        Parses an arithmetic expression from the token list.
        
        Returns:
            ParseResult: The result of parsing the arithmetic expression.
        """
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def term(self):
        """
        Parses a term from the token list.
        
        Returns:
            ParseResult: The result of parsing the term.
        """
        return self.bin_op(self.factor, (TT_MUL, TT_DIV,TT_MOD))

    def factor(self):
        """
        Parses a factor from the token list.
        
        Returns:
            ParseResult: The result of parsing the factor.
        """
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):  
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def power(self):
        """
        Parses a power expression from the token list.
        
        Returns:
            ParseResult: The result of parsing the power expression.
        """
        return self.bin_op(self.call, (TT_POW, ), self.factor)

    def call(self):
        """
        Parses a function call from the token list.
        
        Returns:
            ParseResult: The result of parsing the function call.
        """
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error: return res

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ',' or ')'"
                    ))

                res.register_advancement()
                self.advance()

            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def atom(self):
        """
        Parses an atom (basic unit) from the token list.
        
        Returns:
            ParseResult: The result of parsing the atom.
        """
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))
        
        elif self.current_tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return self.range_expr() if self.peek() == TT_RANGE else super().atom()

        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))

        elif tok.type == TT_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error: return res
            return res.success(list_expr)
        
        elif tok.matches(TT_KEYWORD, 'check'):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        elif tok.matches(TT_KEYWORD, 'each'):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)

        elif tok.matches(TT_KEYWORD, 'chase'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)

        elif tok.matches(TT_KEYWORD, 'mission'):
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, identifier, '+', '-', '(', '[', check', 'each', 'chase', 'mission'"
        ))


    def list_expr(self):
        """
        Parses a list expression from the token list, supporting nested structures.

        Returns:
            ParseResult: The result of parsing the list expression.
        """
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT_LSQUARE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '['"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                element_nodes.append(res.register(self.expr()))
                if res.error:
                    return res

            if self.current_tok.type != TT_RSQUARE:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ',' or ']'"
                ))

            res.register_advancement()
            self.advance()

        return res.success(ListNode(element_nodes, pos_start, self.current_tok.pos_end.copy()))


    def if_expr(self):
        """
        Parses an if statement from the token list.
        
        Returns:
            ParseResult: The result of parsing the if statement.
        """
        res = ParseResult()

      
        if not self.current_tok.matches(TT_KEYWORD, 'check'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'check'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{' to start block"
            ))

        res.register_advancement()
        self.advance()

       
        body = res.register(self.statements())
        if res.error: return res

        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}' to end block"
            ))

        res.register_advancement()
        self.advance()

        
        followups = []
        else_case = None

        while self.current_tok.matches(TT_KEYWORD, 'followup'):
            res.register_advancement()
            self.advance()

            followup_condition = res.register(self.expr())
            if res.error: return res

            if self.current_tok.type != TT_LCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '{' to start block"
                ))

            res.register_advancement()
            self.advance()

            followup_body = res.register(self.statements())
            if res.error: return res

            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}' to end block"
                ))

            res.register_advancement()
            self.advance()
            followups.append((followup_condition, followup_body, False))
            

        if self.current_tok.matches(TT_KEYWORD, 'otherwise'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_LCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '{' to start block"
                ))

            res.register_advancement()
            self.advance()

            else_case_node = res.register(self.statements())
            if res.error: return res

            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}' to end block"
                ))

            res.register_advancement()
            self.advance()
            else_case = else_case_node.element_nodes if isinstance(else_case_node, ListNode) else []

        return res.success(IfNode([(condition, body, True)] + followups, else_case))

    def if_expr_b(self):
        """
        Parses a followup case in an if statement from the token list.
        
        Returns:
            ParseResult: The result of parsing the followup case.
        """
        return self.if_expr_cases('followup')
    
    def if_expr_c(self):
        """
        Parses an otherwise case in an if statement from the token list.
        
        Returns:
            ParseResult: The result of parsing the otherwise case.
        """
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(TT_KEYWORD, 'otherwise'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_LCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '{' to open block"
                ))

            res.register_advancement()
            self.advance()


            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            body = res.register(self.statements())
            if res.error: return res

        
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}' to close block"
                ))

            res.register_advancement()
            self.advance()
            else_case = (body, True)

        return res.success(else_case)

    def if_expr_b_or_c(self):
        """
        Parses followup and otherwise cases in an if statement from the token list.
        
        Returns:
            ParseResult: The result of parsing the followup and otherwise cases.
        """
        res = ParseResult()
        cases, else_case = [], None

        
        while self.current_tok.matches(TT_KEYWORD, 'followup'):
            res.register_advancement()
            self.advance()

            condition = res.register(self.expr())
            if res.error: return res

            if self.current_tok.type != TT_LCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '{' to open block"
                ))

            res.register_advancement()
            self.advance()

            
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            body = res.register(self.statements())
            if res.error: return res

            
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}' to close block"
                ))

            res.register_advancement()
            self.advance()
            cases.append((condition, body, True))

        
        if self.current_tok.matches(TT_KEYWORD, 'otherwise'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_LCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '{' to open block"
                ))

            res.register_advancement()
            self.advance()


            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            else_body = res.register(self.statements())
            if res.error: return res

            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}' to close block"
                ))

            res.register_advancement()
            self.advance()
            else_case = (else_body, True)

        return res.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        """
        Parses cases in an if statement from the token list.
        
        Args:
            case_keyword (str): The keyword representing the case (e.g., 'followup').
        
        Returns:
            ParseResult: The result of parsing the cases.
        """
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT_KEYWORD, case_keyword):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{case_keyword}'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Invalid condition in 'check' statement"
        ))

        
        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{' to start the block"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))

            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}' to close the block"
                ))

            res.register_advancement()
            self.advance()

        else:
            expr = res.register(self.statement())
            if res.error: return res
            cases.append((condition, expr, False))

        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}' to close the block"
            ))

        res.register_advancement()
        self.advance()

        
        all_cases = res.register(self.if_expr_b_or_c())
        if res.error: return res
        new_cases, else_case = all_cases
        cases.extend(new_cases)

        return res.success((cases, else_case))


    def for_expr(self):
        """
        Parses a for loop from the token list, enabling iteration over lists, strings, ranges, and nested structures.
        
        Returns:
            ParseResult: The result of parsing the for loop.
        """
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'each'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'each'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected identifier"
            ))
        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if not self.current_tok.matches(TT_KEYWORD, 'in'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'in'"
            ))
        res.register_advancement()
        self.advance()

    
        if self.current_tok.type == TT_LPAREN:
            iterable = res.register(self.range_expr())  
        else:
            iterable = res.register(self.expr())  

        if res.error:
            return res

        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{' to start block"
            ))
        res.register_advancement()
        self.advance()

    
        body = res.register(self.statements())
        if res.error:
            return res

        
        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}' to end block"
            ))
        res.register_advancement()
        self.advance()

        return res.success(ForNode(var_name, iterable, None, None, body, True))

    def while_expr(self):
        """
        Parses a while loop from the token list.
        
        Returns:
            ParseResult: The result of parsing the while loop.
        """
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'chase'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'chase'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{' "
            ))

        res.register_advancement()
        self.advance()

        body = None
        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()
            body = res.register(self.statements())
            if res.error: return res
        else:
            body = res.register(self.statement())
            if res.error: return res

        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}' "
            ))

        res.register_advancement()
        self.advance()

        return res.success(WhileNode(condition, body, True))

    def func_def(self):
        """
        Parses a function definition from the token list.
        
        Returns:
            ParseResult: The result of parsing the function definition.
        """
        res = ParseResult()

        
        if not self.current_tok.matches(TT_KEYWORD, 'mission'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'mission'"
            ))

        res.register_advancement()
        self.advance()

    
        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
        else:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected function name"
            ))

        if self.current_tok.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '('"
            ))

        res.register_advancement()
        self.advance()
        arg_name_toks = []

        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected identifier"
                    ))
                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

        if self.current_tok.type != TT_RPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ')'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{'"
            ))

        res.register_advancement()
        self.advance()

        body = res.register(self.statements())
        if res.error:
            return res

        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}'"
            ))

        res.register_advancement()
        self.advance()

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, body, False))

    ###################################

    def bin_op(self, func_a, ops, func_b=None):
        """
        Parses a binary operation from the token list.
        
        Args:
            func_a (function): The function to parse the left operand.
            ops (tuple): A tuple of operator types to match.
            func_b (function): The function to parse the right operand. Defaults to func_a.
        
        Returns:
            ParseResult: The result of parsing the binary operation.
        """
        if func_b == None:
            func_b = func_a
        
        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)