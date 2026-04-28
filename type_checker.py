from __future__ import annotations

from PJPVisitor import PJPVisitor


class TypeCheckerVisitor(PJPVisitor):
    def __init__(self) -> None:
        self.symbol_table: dict[str, str] = {}
        self.node_types: dict[object, str] = {}
        self.errors: list[str] = []

    def error(self, ctx, message: str) -> None:
        self.errors.append(f"Type error at {ctx.start.line}:{ctx.start.column}: {message}")

    def remember(self, ctx, value_type: str | None) -> str | None:
        if value_type is not None:
            self.node_types[ctx] = value_type
        return value_type

    def numeric_result(self, left_type: str, right_type: str) -> str:
        return "float" if "float" in {left_type, right_type} else "int"

    def is_assignable(self, target_type: str, value_type: str) -> bool:
        return target_type == value_type or (target_type == "float" and value_type == "int")

    def visitProgram(self, ctx):  
        for statement in ctx.statement():
            self.visit(statement)
        return self.errors

    def visitEmptyStatement(self, ctx):  
        return None

    def visitDeclarationStatement(self, ctx):  
        declared_type = ctx.typeSpec().getText()
        for token in ctx.identifierList().IDENTIFIER():
            name = token.getText()
            if name in self.symbol_table:
                self.error(ctx, f"variable '{name}' is already declared")
            else:
                self.symbol_table[name] = declared_type
        return None

    def visitReadStatement(self, ctx):  
        for token in ctx.identifierList().IDENTIFIER():
            name = token.getText()
            if name not in self.symbol_table:
                self.error(ctx, f"variable '{name}' is not declared")
                continue
            if self.symbol_table[name] == "file":
                self.error(ctx, f"read does not support variable '{name}' of type file")
        return None

    def visitWriteStatement(self, ctx):  
        for expression in ctx.expressionList().expression():
            expr_type = self.visit(expression)
            if expr_type == "file":
                self.error(expression, "write does not support values of type file")
        return None
    
    def visitFwriteStatement(self, ctx):
        name = ctx.IDENTIFIER().getText()

        if name not in self.symbol_table:
            self.error(ctx, f"variable '{name}' is not declared")
            return None
    
        if self.symbol_table[name] != "file":
            self.error(ctx, f"variable '{name}' must have type file in fwrite")
            return None

        for expr in ctx.expression():
            expr_type = self.visit(expr)
            if expr_type == "file":
                self.error(ctx, "cannot write value of type file into a file")
        return None
    

    def visitBlockStatement(self, ctx):  
        for statement in ctx.statement():
            self.visit(statement)
        return None

    def visitIfStatement(self, ctx):  
        condition_type = self.visit(ctx.expression())
        if condition_type is not None and condition_type != "bool":
            self.error(ctx.expression(), "if condition must have type bool")
        self.visit(ctx.statement(0))
        if len(ctx.statement()) > 1:
            self.visit(ctx.statement(1))
        return None

    def visitWhileStatement(self, ctx):  
        condition_type = self.visit(ctx.expression())
        if condition_type is not None and condition_type != "bool":
            self.error(ctx.expression(), "while condition must have type bool")
        self.visit(ctx.statement())
        return None

    def visitExpressionStatement(self, ctx): 
        self.visit(ctx.expression())
        return None
    
    def visitFopenStatement(self, ctx):
        name = ctx.IDENTIFIER().getText()

        if name not in self.symbol_table:
            self.error(ctx, f"variable '{name}' is not declared")
            return None

        if self.symbol_table[name] != "file":
            self.error(ctx, f"variable '{name}' must have type file in fopen")
            return None
        return None
        
    def visitFileWriteStatement(self, ctx):
        name = ctx.IDENTIFIER().getText()

        if name not in self.symbol_table:
            self.error(ctx, f"variable '{name}' is not declared")
            return None

        if self.symbol_table[name] != "file":
            self.error(ctx, f"variable '{name}' must have type file for '<<'")
            return None

        for expr in ctx.expression():
            expr_type = self.visit(expr)
            if expr_type == "file":
                self.error(ctx, "cannot write value of type file into a file")

        return None


    def visitAssignment(self, ctx): 
        name = ctx.IDENTIFIER().getText()
        value_type = self.visit(ctx.assignmentExpression())
        target_type = self.symbol_table.get(name)

        if target_type is None:
            self.error(ctx, f"variable '{name}' is not declared")
            return None
        
        if target_type == "file":
            self.error(ctx, "assignment to values of type file is not supported")
            return None

        if value_type == "file":
            self.error(ctx, "cannot assign value of type file")
            return None

        if value_type is not None and not self.is_assignable(target_type, value_type):
            self.error(ctx, f"cannot assign value of type {value_type} to variable '{name}' of type {target_type}")
        
        return self.remember(ctx, target_type)

    def visitAssignmentPassthrough(self, ctx):  
        return self.remember(ctx, self.visit(ctx.logicalOrExpression()))

    def visitLogicalOr(self, ctx):  
        left_type = self.visit(ctx.logicalOrExpression())
        right_type = self.visit(ctx.logicalAndExpression())
        if left_type == right_type == "bool":
            return self.remember(ctx, "bool")
        if left_type is not None and right_type is not None:
            self.error(ctx, "operator '||' expects bool operands")
        return None

    def visitLogicalOrPassthrough(self, ctx):  
        return self.remember(ctx, self.visit(ctx.logicalAndExpression()))

    def visitLogicalAnd(self, ctx):  
        left_type = self.visit(ctx.logicalAndExpression())
        right_type = self.visit(ctx.equalityExpression())
        if left_type == right_type == "bool":
            return self.remember(ctx, "bool")
        if left_type is not None and right_type is not None:
            self.error(ctx, "operator '&&' expects bool operands")
        return None

    def visitLogicalAndPassthrough(self, ctx):
        return self.remember(ctx, self.visit(ctx.equalityExpression()))

    def visitEquality(self, ctx):  
        left_type = self.visit(ctx.equalityExpression())
        right_type = self.visit(ctx.relationalExpression())
        if left_type is None or right_type is None:
            return None
        if left_type in {"int", "float"} and right_type in {"int", "float"}:
            return self.remember(ctx, "bool")
        if left_type == right_type and left_type == "string":
            return self.remember(ctx, "bool")
        self.error(ctx, f"operator '{ctx.op.text}' expects compatible int, float, or string operands")
        return None

    def visitEqualityPassthrough(self, ctx):  
        return self.remember(ctx, self.visit(ctx.relationalExpression()))

    def visitRelational(self, ctx):  
        left_type = self.visit(ctx.relationalExpression())
        right_type = self.visit(ctx.additiveExpression())
        if left_type in {"int", "float"} and right_type in {"int", "float"}:
            return self.remember(ctx, "bool")
        if left_type is not None and right_type is not None:
            self.error(ctx, f"operator '{ctx.op.text}' expects numeric operands")
        return None

    def visitRelationalPassthrough(self, ctx):  
        return self.remember(ctx, self.visit(ctx.additiveExpression()))

    def visitAdditive(self, ctx):  
        left_type = self.visit(ctx.additiveExpression())
        right_type = self.visit(ctx.multiplicativeExpression())
        operator = ctx.op.text
        if left_type is None or right_type is None:
            return None
        if operator == ".":
            if left_type == right_type == "string":
                return self.remember(ctx, "string")
            self.error(ctx, "operator '.' expects string operands")
            return None
        if left_type in {"int", "float"} and right_type in {"int", "float"}:
            return self.remember(ctx, self.numeric_result(left_type, right_type))
        self.error(ctx, f"operator '{operator}' expects numeric operands")
        return None

    def visitAdditivePassthrough(self, ctx):  
        return self.remember(ctx, self.visit(ctx.multiplicativeExpression()))

    def visitMultiplicative(self, ctx):  
        left_type = self.visit(ctx.multiplicativeExpression())
        right_type = self.visit(ctx.unaryExpression())
        operator = ctx.op.text
        if left_type is None or right_type is None:
            return None
        if operator == "%":
            if left_type == right_type == "int":
                return self.remember(ctx, "int")
            self.error(ctx, "operator '%' expects int operands")
            return None
        if left_type in {"int", "float"} and right_type in {"int", "float"}:
            return self.remember(ctx, self.numeric_result(left_type, right_type))
        self.error(ctx, f"operator '{operator}' expects numeric operands")
        return None

    def visitMultiplicativePassthrough(self, ctx):  
        return self.remember(ctx, self.visit(ctx.unaryExpression()))

    def visitLogicalNot(self, ctx):  
        operand_type = self.visit(ctx.unaryExpression())
        if operand_type == "bool":
            return self.remember(ctx, "bool")
        if operand_type is not None:
            self.error(ctx, "operator '!' expects bool operand")
        return None

    def visitUnaryMinus(self, ctx):  
        operand_type = self.visit(ctx.unaryExpression())
        if operand_type in {"int", "float"}:
            return self.remember(ctx, operand_type)
        if operand_type is not None:
            self.error(ctx, "unary '-' expects int or float")
        return None

    def visitUnaryPassthrough(self, ctx):  
        return self.remember(ctx, self.visit(ctx.primaryExpression()))

    def visitLiteralPrimary(self, ctx):  
        return self.remember(ctx, self.visit(ctx.literal()))

    def visitIdentifierPrimary(self, ctx):  
        name = ctx.IDENTIFIER().getText()
        declared_type = self.symbol_table.get(name)
        if declared_type is None:
            self.error(ctx, f"variable '{name}' is not declared")
            return None
        return self.remember(ctx, declared_type)

    def visitParenPrimary(self, ctx):  
        return self.remember(ctx, self.visit(ctx.expression()))

    def visitLiteral(self, ctx):  
        if ctx.INT_LITERAL():
            return self.remember(ctx, "int")
        if ctx.FLOAT_LITERAL():
            return self.remember(ctx, "float")
        if ctx.BOOL_LITERAL():
            return self.remember(ctx, "bool")
        return self.remember(ctx, "string")
    
