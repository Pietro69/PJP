# PJP Extensions Cheatsheet

Tento subor je rychly tahak pre pripad, ze profak zada doplnenie novej feature do aktualneho projektu.

Zakladne pravidlo:

1. uprav `PJP.g4`
2. spusti `py -3.13 generate_parser.py`
3. dopln `type_checker.py`
4. dopln `code_generator.py`
5. ak pribudne nova instrukcia, dopln `interpreter.py`

Nikdy needituj rucne:
- `PJPLexer.py`
- `PJPParser.py`
- `PJPVisitor.py`

---

## do-while

### Subory
- `PJP.g4`
- `type_checker.py`
- `code_generator.py`

### `PJP.g4`
Do `statement` pridaj:

```g4
| 'do' statement 'while' '(' expression ')' ';'              #doWhileStatement
```

### `type_checker.py`
Do `TypeCheckerVisitor` pridaj:

```python
def visitDoWhileStatement(self, ctx):
    self.visit(ctx.statement())
    condition_type = self.visit(ctx.expression())
    if condition_type is not None and condition_type != "bool":
        self.error(ctx.expression(), "do-while condition must have type bool")
    return None
```

### `code_generator.py`
Do `CodeGeneratorVisitor` pridaj:

```python
def visitDoWhileStatement(self, ctx):
    start_label = self.new_label()
    end_label = self.new_label()

    self.emit(f"label {start_label}")
    self.visit(ctx.statement())
    self.visit(ctx.expression())
    self.emit(f"fjmp {end_label}")
    self.emit(f"jmp {start_label}")
    self.emit(f"label {end_label}")
    return None
```

### Interpreter
Netreba menit.

---

## for

### Subory
- `PJP.g4`
- `type_checker.py`
- `code_generator.py`

### `PJP.g4`
Do `statement` pridaj:

```g4
| 'for' '(' expression ';' expression ';' expression ')' statement   #forStatement
```

### `type_checker.py`

```python
def visitForStatement(self, ctx):
    self.visit(ctx.expression(0))
    condition_type = self.visit(ctx.expression(1))
    if condition_type is not None and condition_type != "bool":
        self.error(ctx.expression(1), "for condition must have type bool")
    self.visit(ctx.expression(2))
    self.visit(ctx.statement())
    return None
```

### `code_generator.py`

```python
def visitForStatement(self, ctx):
    start_label = self.new_label()
    end_label = self.new_label()

    self.visit(ctx.expression(0))
    self.emit("pop")

    self.emit(f"label {start_label}")
    self.visit(ctx.expression(1))
    self.emit(f"fjmp {end_label}")

    self.visit(ctx.statement())

    self.visit(ctx.expression(2))
    self.emit("pop")

    self.emit(f"jmp {start_label}")
    self.emit(f"label {end_label}")
    return None
```

### Interpreter
Netreba menit.

---

## ternary `?:`

### Subory
- `PJP.g4`
- `type_checker.py`
- `code_generator.py`

### `PJP.g4`
Zmen `assignmentExpression` a pridaj `ternaryExpression`:

```g4
assignmentExpression
    : IDENTIFIER '=' assignmentExpression                        #assignment
    | ternaryExpression                                          #assignmentPassthrough
    ;

ternaryExpression
    : logicalOrExpression ('?' expression ':' ternaryExpression)? #ternaryExpressionRule
    ;
```

### `type_checker.py`

```python
def visitTernaryExpressionRule(self, ctx):
    if ctx.getChildCount() == 1:
        return self.remember(ctx, self.visit(ctx.logicalOrExpression()))

    cond_type = self.visit(ctx.logicalOrExpression())
    true_type = self.visit(ctx.expression())
    false_type = self.visit(ctx.ternaryExpression())

    if cond_type is not None and cond_type != "bool":
        self.error(ctx, "ternary condition must have type bool")
        return None

    if true_type == false_type:
        return self.remember(ctx, true_type)

    if {true_type, false_type} == {"int", "float"}:
        return self.remember(ctx, "float")

    self.error(ctx, "ternary branches must have compatible types")
    return None
```

### `code_generator.py`

```python
def visitTernaryExpressionRule(self, ctx):
    if ctx.getChildCount() == 1:
        return self.visit(ctx.logicalOrExpression())

    false_label = self.new_label()
    end_label = self.new_label()

    overall_type = self.node_types[ctx]
    true_node = ctx.expression()
    false_node = ctx.ternaryExpression()

    self.visit(ctx.logicalOrExpression())
    self.emit(f"fjmp {false_label}")

    self.visit(true_node)
    if self.node_types[true_node] == "int" and overall_type == "float":
        self.emit("itof")
    self.emit(f"jmp {end_label}")

    self.emit(f"label {false_label}")
    self.visit(false_node)
    if self.node_types[false_node] == "int" and overall_type == "float":
        self.emit("itof")

    self.emit(f"label {end_label}")
    return None
```

### Interpreter
Netreba menit.

---

## string indexacia `text[i]`

### Subory
- `PJP.g4`
- `type_checker.py`
- `code_generator.py`
- `interpreter.py`

### `PJP.g4`
Pridaj postfix vrstvu:

```g4
postfixExpression
    : primaryExpression ('[' expression ']')*                    #postfixIndex
    ;
```

A v `unaryExpression` pouzi:

```g4
| postfixExpression                                             #unaryPassthrough
```

### `type_checker.py`

```python
def visitPostfixIndex(self, ctx):
    current_type = self.visit(ctx.primaryExpression())

    for expr_ctx in ctx.expression():
        index_type = self.visit(expr_ctx)
        if current_type != "string":
            self.error(ctx, "can only index strings")
            return None
        if index_type != "int":
            self.error(ctx, "string index must have type int")
            return None
        current_type = "string"

    return self.remember(ctx, current_type)
```

### `code_generator.py`

```python
def visitPostfixIndex(self, ctx):
    self.visit(ctx.primaryExpression())
    for expr_ctx in ctx.expression():
        self.visit(expr_ctx)
        self.emit("getchar")
    return None
```

### `interpreter.py`

```python
elif command == "getchar":
    idx = self.stack.pop()
    text = self.stack.pop()
    self.stack.append(text[idx])
```

---

## `+=`, `-=`, `*=`

### Subory
- `PJP.g4`
- `type_checker.py`
- `code_generator.py`

### `PJP.g4`
Zmen `assignmentExpression`:

```g4
assignmentExpression
    : IDENTIFIER op=('=' | '+=' | '-=' | '*=') assignmentExpression   #assignment
    | ternaryExpression                                                #assignmentPassthrough
    ;
```

### `type_checker.py`
Do `visitAssignment` pridaj pracu s `op = ctx.op.text`.

Pre rozsirene assignmenty:

```python
op = ctx.op.text

if op in {"+=", "-=", "*="}:
    if target_type == "file" or value_type == "file":
        self.error(ctx, f"operator '{op}' does not support file")
        return None
    if target_type not in {"int", "float"} or value_type not in {"int", "float"}:
        self.error(ctx, f"operator '{op}' expects numeric operands")
        return None
    result_type = "float" if "float" in {target_type, value_type} else "int"
    return self.remember(ctx, result_type)
```

### `code_generator.py`
V `visitAssignment` rozsir podla `op = ctx.op.text`:

```python
elif op in {"+=", "-=", "*="}:
    self.emit(f"load {name}")
    self.visit(right_ctx)

    left_type = self.symbol_table[name]
    right_type = self.node_types[right_ctx]
    overall_type = "float" if "float" in {left_type, right_type} else "int"

    if left_type == "int" and overall_type == "float":
        self.emit("itof")
    if right_type == "int" and overall_type == "float":
        self.emit("itof")

    opcode = {"+=": "add", "-=": "sub", "*=": "mul"}[op]
    self.emit(f"{opcode} {'F' if overall_type == 'float' else 'I'}")
    self.emit(f"save {name}")
    self.emit(f"load {name}")
    return None
```

### Interpreter
Netreba menit.

---

## `++`, `--`

### Subory
- `PJP.g4`
- `type_checker.py`
- `code_generator.py`

### `PJP.g4`
Najlahsie ako statement:

```g4
| IDENTIFIER '++' ';'                                           #incrementStatement
| IDENTIFIER '--' ';'                                           #decrementStatement
```

### `type_checker.py`

```python
def visitIncrementStatement(self, ctx):
    name = ctx.IDENTIFIER().getText()
    declared_type = self.symbol_table.get(name)
    if declared_type is None:
        self.error(ctx, f"variable '{name}' is not declared")
        return None
    if declared_type not in {"int", "float"}:
        self.error(ctx, "++ expects int or float variable")
    return None

def visitDecrementStatement(self, ctx):
    name = ctx.IDENTIFIER().getText()
    declared_type = self.symbol_table.get(name)
    if declared_type is None:
        self.error(ctx, f"variable '{name}' is not declared")
        return None
    if declared_type not in {"int", "float"}:
        self.error(ctx, "-- expects int or float variable")
    return None
```

### `code_generator.py`

```python
def visitIncrementStatement(self, ctx):
    name = ctx.IDENTIFIER().getText()
    declared_type = self.symbol_table[name]
    self.emit(f"load {name}")
    self.emit(f"push {'F 1.0' if declared_type == 'float' else 'I 1'}")
    self.emit(f"add {'F' if declared_type == 'float' else 'I'}")
    self.emit(f"save {name}")
    return None

def visitDecrementStatement(self, ctx):
    name = ctx.IDENTIFIER().getText()
    declared_type = self.symbol_table[name]
    self.emit(f"load {name}")
    self.emit(f"push {'F 1.0' if declared_type == 'float' else 'I 1'}")
    self.emit(f"sub {'F' if declared_type == 'float' else 'I'}")
    self.emit(f"save {name}")
    return None
```

### Interpreter
Netreba menit.

---

## `&`, `|`, `^`

### Subory
- `PJP.g4`
- `type_checker.py`
- `code_generator.py`
- `interpreter.py`

### `PJP.g4`
Pridaj novy level:

```g4
bitwiseExpression
    : bitwiseExpression op=('&' | '|' | '^') equalityExpression   #bitwise
    | equalityExpression                                           #bitwisePassthrough
    ;
```

A `logicalAndExpression` nech pouziva `bitwiseExpression`.

### `type_checker.py`

```python
def visitBitwise(self, ctx):
    left_type = self.visit(ctx.bitwiseExpression())
    right_type = self.visit(ctx.equalityExpression())
    if left_type == right_type == "int":
        return self.remember(ctx, "int")
    self.error(ctx, f"operator '{ctx.op.text}' expects int operands")
    return None

def visitBitwisePassthrough(self, ctx):
    return self.remember(ctx, self.visit(ctx.equalityExpression()))
```

### `code_generator.py`

```python
def visitBitwise(self, ctx):
    self.visit(ctx.bitwiseExpression())
    self.visit(ctx.equalityExpression())
    opcode = {"&": "band", "|": "bor", "^": "bxor"}[ctx.op.text]
    self.emit(opcode)
    return None

def visitBitwisePassthrough(self, ctx):
    return self.visit(ctx.equalityExpression())
```

### `interpreter.py`

```python
elif command == "band":
    right = self.stack.pop()
    left = self.stack.pop()
    self.stack.append(left & right)

elif command == "bor":
    right = self.stack.pop()
    left = self.stack.pop()
    self.stack.append(left | right)

elif command == "bxor":
    right = self.stack.pop()
    left = self.stack.pop()
    self.stack.append(left ^ right)
```

---

## FILE / `fopen` / `fwrite`

### Aktualny stav projektu
Toto uz mas v projekte:

Source:

```c
file f;
fopen f "soubor.txt";
fwrite f, "abc", 1 + 2;
```

Generovane instrukcie:

```text
fopen f "soubor.txt"
push S "abc"
fwrite f
push I 1
push I 2
add I
fwrite f
```

### Ak profak chce uppercase `FILE`
V `PJP.g4` najlahsie podpor oboje:

```g4
typeSpec
    : 'int'
    | 'float'
    | 'bool'
    | 'string'
    | 'file'
    | 'FILE'
    ;
```

Ak chces, mozes potom v `type_checker.py` pri deklaracii normalizovat:

```python
declared_type = ctx.typeSpec().getText().lower()
```

### Ak profak chce `f << x`
To uz mas ako statement:

```g4
| IDENTIFIER '<<' expression ('<<' expression)* ';'          #fileWriteStatement
```

### Druhe zadanie: instruction-based `open` a `fwrite 2`
Toto zatial implementovane nie je.

To by bol iny format napr.:

```text
push S "soubor.txt"
open
save f
load f
push S "abc"
push I 1
push I 2
add I
fwrite 2
```

Na to by bolo treba dorobit nove opcode v `interpreter.py`.

---

## Rychla mapa obtiaznosti

- `do-while`: lahke
- `for`: lahke
- `+= -= *=`: lahke az stredne
- `++ --`: lahke
- ternary: stredne
- string indexacia: stredne
- `& | ^`: stredne az tazsie
- instruction-based `open` / `fwrite 2`: tazsie, lebo menis model instrukcii

