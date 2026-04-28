grammar PJP;

program
    : statement* EOF
    ;

statement
    : ';'                                                        #emptyStatement
    | typeSpec identifierList ';'                                #declarationStatement
    | 'read' identifierList ';'                                  #readStatement
    | 'write' expressionList ';'                                 #writeStatement
    | 'fopen' IDENTIFIER STRING_LITERAL ';'                      #fopenStatement
    | 'fwrite' IDENTIFIER ',' expression (',' expression)* ';'   #fwriteStatement
    | IDENTIFIER '<<' expression ('<<' expression)* ';'          #fileWriteStatement
    | '{' statement* '}'                                         #blockStatement
    | 'if' '(' expression ')' statement ('else' statement)?      #ifStatement
    | 'while' '(' expression ')' statement                       #whileStatement
    | expression ';'                                             #expressionStatement
    ;

typeSpec
    : 'int'
    | 'float'
    | 'bool'
    | 'string'
    | 'file'
    ;

identifierList
    : IDENTIFIER (',' IDENTIFIER)*
    ;

expressionList
    : expression (',' expression)*
    ;

expression
    : assignmentExpression
    ;

assignmentExpression
    : IDENTIFIER '=' assignmentExpression                        #assignment
    | logicalOrExpression                                        #assignmentPassthrough
    ;

logicalOrExpression
    : logicalOrExpression '||' logicalAndExpression              #logicalOr
    | logicalAndExpression                                       #logicalOrPassthrough
    ;

logicalAndExpression
    : logicalAndExpression '&&' equalityExpression               #logicalAnd
    | equalityExpression                                         #logicalAndPassthrough
    ;

equalityExpression
    : equalityExpression op=('==' | '!=') relationalExpression   #equality
    | relationalExpression                                       #equalityPassthrough
    ;

relationalExpression
    : relationalExpression op=('<' | '>') additiveExpression     #relational
    | additiveExpression                                         #relationalPassthrough
    ;

additiveExpression
    : additiveExpression op=('+' | '-' | '.') multiplicativeExpression #additive
    | multiplicativeExpression                                        #additivePassthrough
    ;

multiplicativeExpression
    : multiplicativeExpression op=('*' | '/' | '%') unaryExpression #multiplicative
    | unaryExpression                                               #multiplicativePassthrough
    ;

unaryExpression
    : '!' unaryExpression                                        #logicalNot
    | '-' unaryExpression                                        #unaryMinus
    | primaryExpression                                          #unaryPassthrough
    ;

primaryExpression
    : literal                                                    #literalPrimary
    | IDENTIFIER                                                 #identifierPrimary
    | '(' expression ')'                                         #parenPrimary
    ;

literal
    : INT_LITERAL
    | FLOAT_LITERAL
    | BOOL_LITERAL
    | STRING_LITERAL
    ;

BOOL_LITERAL
    : 'true'
    | 'false'
    ;

FLOAT_LITERAL
    : [0-9]+ '.' [0-9]+
    ;

INT_LITERAL
    : [0-9]+
    ;

STRING_LITERAL
    : '"' ( '\\' . | ~["\\\r\n] )* '"'
    ;

IDENTIFIER
    : [A-Za-z] [A-Za-z0-9]*
    ;

COMMENT
    : '//' ~[\r\n]* -> skip
    ;

WS
    : [ \t\r\n]+ -> skip
    ;
