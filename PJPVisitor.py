# Generated from D:/PJP/PJP.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .PJPParser import PJPParser
else:
    from PJPParser import PJPParser

# This class defines a complete generic visitor for a parse tree produced by PJPParser.

class PJPVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PJPParser#program.
    def visitProgram(self, ctx:PJPParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#emptyStatement.
    def visitEmptyStatement(self, ctx:PJPParser.EmptyStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#declarationStatement.
    def visitDeclarationStatement(self, ctx:PJPParser.DeclarationStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#readStatement.
    def visitReadStatement(self, ctx:PJPParser.ReadStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#writeStatement.
    def visitWriteStatement(self, ctx:PJPParser.WriteStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#fopenStatement.
    def visitFopenStatement(self, ctx:PJPParser.FopenStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#fwriteStatement.
    def visitFwriteStatement(self, ctx:PJPParser.FwriteStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#fileWriteStatement.
    def visitFileWriteStatement(self, ctx:PJPParser.FileWriteStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#blockStatement.
    def visitBlockStatement(self, ctx:PJPParser.BlockStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#ifStatement.
    def visitIfStatement(self, ctx:PJPParser.IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#whileStatement.
    def visitWhileStatement(self, ctx:PJPParser.WhileStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#expressionStatement.
    def visitExpressionStatement(self, ctx:PJPParser.ExpressionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#typeSpec.
    def visitTypeSpec(self, ctx:PJPParser.TypeSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#identifierList.
    def visitIdentifierList(self, ctx:PJPParser.IdentifierListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#expressionList.
    def visitExpressionList(self, ctx:PJPParser.ExpressionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#expression.
    def visitExpression(self, ctx:PJPParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#assignment.
    def visitAssignment(self, ctx:PJPParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#assignmentPassthrough.
    def visitAssignmentPassthrough(self, ctx:PJPParser.AssignmentPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#logicalOrPassthrough.
    def visitLogicalOrPassthrough(self, ctx:PJPParser.LogicalOrPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#logicalOr.
    def visitLogicalOr(self, ctx:PJPParser.LogicalOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#logicalAndPassthrough.
    def visitLogicalAndPassthrough(self, ctx:PJPParser.LogicalAndPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#logicalAnd.
    def visitLogicalAnd(self, ctx:PJPParser.LogicalAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#equalityPassthrough.
    def visitEqualityPassthrough(self, ctx:PJPParser.EqualityPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#equality.
    def visitEquality(self, ctx:PJPParser.EqualityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#relationalPassthrough.
    def visitRelationalPassthrough(self, ctx:PJPParser.RelationalPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#relational.
    def visitRelational(self, ctx:PJPParser.RelationalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#additivePassthrough.
    def visitAdditivePassthrough(self, ctx:PJPParser.AdditivePassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#additive.
    def visitAdditive(self, ctx:PJPParser.AdditiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#multiplicativePassthrough.
    def visitMultiplicativePassthrough(self, ctx:PJPParser.MultiplicativePassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#multiplicative.
    def visitMultiplicative(self, ctx:PJPParser.MultiplicativeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#logicalNot.
    def visitLogicalNot(self, ctx:PJPParser.LogicalNotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#unaryMinus.
    def visitUnaryMinus(self, ctx:PJPParser.UnaryMinusContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#unaryPassthrough.
    def visitUnaryPassthrough(self, ctx:PJPParser.UnaryPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#literalPrimary.
    def visitLiteralPrimary(self, ctx:PJPParser.LiteralPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#identifierPrimary.
    def visitIdentifierPrimary(self, ctx:PJPParser.IdentifierPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#parenPrimary.
    def visitParenPrimary(self, ctx:PJPParser.ParenPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PJPParser#literal.
    def visitLiteral(self, ctx:PJPParser.LiteralContext):
        return self.visitChildren(ctx)



del PJPParser