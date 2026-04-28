from __future__ import annotations

from PJPVisitor import PJPVisitor


TYPE_TO_CODE = {
    "int": "I",
    "float": "F",
    "bool": "B",
    "string": "S",
}


class CodeGeneratorVisitor(PJPVisitor):
    def __init__(self, symbol_table: dict[str, str], node_types: dict[object, str]) -> None:
        self.symbol_table = symbol_table
        self.node_types = node_types
        self.instructions: list[str] = []
        self.next_label = 0

    def new_label(self) -> int:
        label = self.next_label
        self.next_label += 1
        return label

    def emit(self, instruction: str) -> None:
        self.instructions.append(instruction)

    def cast_if_needed(self, source_type: str, target_type: str) -> None:
        if source_type == "int" and target_type == "float":
            self.emit("itof")

    def numeric_target_type(self, left_ctx, right_ctx) -> str:
        left_type = self.node_types[left_ctx]
        right_type = self.node_types[right_ctx]
        return "float" if "float" in {left_type, right_type} else "int"

    def visitProgram(self, ctx):  
        for statement in ctx.statement():
            self.visit(statement)
        return self.instructions

    def visitEmptyStatement(self, ctx):  
        return None

    def visitDeclarationStatement(self, ctx):  
        declared_type = ctx.typeSpec().getText()
        for token in ctx.identifierList().IDENTIFIER():
            name = token.getText()

            if declared_type == "file":
                continue
            elif declared_type == "int":
                self.emit("push I 0")
            elif declared_type == "float":
                self.emit("push F 0.0")
            elif declared_type == "bool":
                self.emit("push B false")
            else:
                self.emit('push S ""')
            self.emit(f"save {name}")
        return None
    
    def visitFopenStatement(self, ctx):  
        name = ctx.IDENTIFIER().getText()
        path = ctx.STRING_LITERAL().getText()
        self.emit(f"fopen {name} {path}")
        return None
    
    def visitFileWriteStatement(self, ctx):  
        name = ctx.IDENTIFIER().getText()

        for expr in ctx.expression():
            self.visit(expr)
            self.emit(f"fwrite {name}")

        return None

    def visitReadStatement(self, ctx):  
        for token in ctx.identifierList().IDENTIFIER():
            name = token.getText()
            self.emit(f"read {TYPE_TO_CODE[self.symbol_table[name]]}")
            self.emit(f"save {name}")
        return None

    def visitWriteStatement(self, ctx):  
        expressions = ctx.expressionList().expression()
        for expression in expressions:
            self.visit(expression)
        self.emit(f"print {len(expressions)}")
        return None
    
    def visitFwriteStatement(self, ctx):
        name = ctx.IDENTIFIER().getText()

        for expr in ctx.expression():
            self.visit(expr)
            self.emit(f"fwrite {name}")

        return None

    def visitBlockStatement(self, ctx):  
        for statement in ctx.statement():
            self.visit(statement)
        return None

    def visitIfStatement(self, ctx):  
        else_label = self.new_label()
        end_label = self.new_label()
        self.visit(ctx.expression())
        self.emit(f"fjmp {else_label}")
        self.visit(ctx.statement(0))
        self.emit(f"jmp {end_label}")
        self.emit(f"label {else_label}")
        if len(ctx.statement()) > 1:
            self.visit(ctx.statement(1))
        self.emit(f"label {end_label}")
        return None

    def visitWhileStatement(self, ctx):  
        start_label = self.new_label()
        end_label = self.new_label()
        self.emit(f"label {start_label}")
        self.visit(ctx.expression())
        self.emit(f"fjmp {end_label}")
        self.visit(ctx.statement())
        self.emit(f"jmp {start_label}")
        self.emit(f"label {end_label}")
        return None

    def visitExpressionStatement(self, ctx):  
        self.visit(ctx.expression())
        self.emit("pop")
        return None

    def visitAssignment(self, ctx):  
        name = ctx.IDENTIFIER().getText()
        right_ctx = ctx.assignmentExpression()
        self.visit(right_ctx)
        self.cast_if_needed(self.node_types[right_ctx], self.symbol_table[name])
        self.emit(f"save {name}")
        self.emit(f"load {name}")
        return None

    def visitAssignmentPassthrough(self, ctx):  
        return self.visit(ctx.logicalOrExpression())

    def visitLogicalOr(self, ctx):  
        self.visit(ctx.logicalOrExpression())
        self.visit(ctx.logicalAndExpression())
        self.emit("or")
        return None

    def visitLogicalOrPassthrough(self, ctx): 
        return self.visit(ctx.logicalAndExpression())

    def visitLogicalAnd(self, ctx):  
        self.visit(ctx.logicalAndExpression())
        self.visit(ctx.equalityExpression())
        self.emit("and")
        return None

    def visitLogicalAndPassthrough(self, ctx):  
        return self.visit(ctx.equalityExpression())

    def visitEquality(self, ctx):  
        left_ctx = ctx.equalityExpression()
        right_ctx = ctx.relationalExpression()
        left_type = self.node_types[left_ctx]
        right_type = self.node_types[right_ctx]
        if left_type in {"int", "float"} and right_type in {"int", "float"}:
            target_type = self.numeric_target_type(left_ctx, right_ctx)
            self.visit(left_ctx)
            self.cast_if_needed(left_type, target_type)
            self.visit(right_ctx)
            self.cast_if_needed(right_type, target_type)
            self.emit(f"eq {TYPE_TO_CODE[target_type]}")
        else:
            self.visit(left_ctx)
            self.visit(right_ctx)
            self.emit(f"eq {TYPE_TO_CODE[left_type]}")
        if ctx.op.text == "!=":
            self.emit("not")
        return None

    def visitEqualityPassthrough(self, ctx): 
        return self.visit(ctx.relationalExpression())

    def visitRelational(self, ctx):  
        left_ctx = ctx.relationalExpression()
        right_ctx = ctx.additiveExpression()
        left_type = self.node_types[left_ctx]
        right_type = self.node_types[right_ctx]
        target_type = self.numeric_target_type(left_ctx, right_ctx)
        self.visit(left_ctx)
        self.cast_if_needed(left_type, target_type)
        self.visit(right_ctx)
        self.cast_if_needed(right_type, target_type)
        self.emit(f"{'lt' if ctx.op.text == '<' else 'gt'} {TYPE_TO_CODE[target_type]}")
        return None

    def visitRelationalPassthrough(self, ctx):  
        return self.visit(ctx.additiveExpression())

    def visitAdditive(self, ctx):  
        left_ctx = ctx.additiveExpression()
        right_ctx = ctx.multiplicativeExpression()
        if ctx.op.text == ".":
            self.visit(left_ctx)
            self.visit(right_ctx)
            self.emit("concat")
            return None
        left_type = self.node_types[left_ctx]
        right_type = self.node_types[right_ctx]
        target_type = self.numeric_target_type(left_ctx, right_ctx)
        self.visit(left_ctx)
        self.cast_if_needed(left_type, target_type)
        self.visit(right_ctx)
        self.cast_if_needed(right_type, target_type)
        opcode = "add" if ctx.op.text == "+" else "sub"
        self.emit(f"{opcode} {TYPE_TO_CODE[target_type]}")
        return None

    def visitAdditivePassthrough(self, ctx):  
        return self.visit(ctx.multiplicativeExpression())

    def visitMultiplicative(self, ctx):  
        left_ctx = ctx.multiplicativeExpression()
        right_ctx = ctx.unaryExpression()
        if ctx.op.text == "%":
            self.visit(left_ctx)
            self.visit(right_ctx)
            self.emit("mod")
            return None
        left_type = self.node_types[left_ctx]
        right_type = self.node_types[right_ctx]
        target_type = self.numeric_target_type(left_ctx, right_ctx)
        self.visit(left_ctx)
        self.cast_if_needed(left_type, target_type)
        self.visit(right_ctx)
        self.cast_if_needed(right_type, target_type)
        opcode = {
            "*": "mul",
            "/": "div",
        }[ctx.op.text]
        self.emit(f"{opcode} {TYPE_TO_CODE[target_type]}")
        return None

    def visitMultiplicativePassthrough(self, ctx):  
        return self.visit(ctx.unaryExpression())

    def visitLogicalNot(self, ctx):  
        self.visit(ctx.unaryExpression())
        self.emit("not")
        return None

    def visitUnaryMinus(self, ctx):  
        self.visit(ctx.unaryExpression())
        self.emit(f"uminus {TYPE_TO_CODE[self.node_types[ctx]]}")
        return None

    def visitUnaryPassthrough(self, ctx):  
        return self.visit(ctx.primaryExpression())

    def visitLiteralPrimary(self, ctx):  
        return self.visit(ctx.literal())

    def visitIdentifierPrimary(self, ctx):  
        self.emit(f"load {ctx.IDENTIFIER().getText()}")
        return None

    def visitParenPrimary(self, ctx):  
        return self.visit(ctx.expression())

    def visitLiteral(self, ctx):  
        if ctx.INT_LITERAL():
            self.emit(f"push I {ctx.getText()}")
        elif ctx.FLOAT_LITERAL():
            self.emit(f"push F {ctx.getText()}")
        elif ctx.BOOL_LITERAL():
            self.emit(f"push B {ctx.getText()}")
        else:
            self.emit(f"push S {ctx.getText()}")
        return None
