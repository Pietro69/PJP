# PJP Compiler and Interpreter

Jednoduchy projekt v jednom priecinku:

- `PJP.g4` - gramatika jazyka
- `generate_parser.py` - vygeneruje lexer, parser a visitor z gramatiky
- `main.py` - hlavny vstupny bod
- `type_checker.py` - semanticka a typova kontrola
- `code_generator.py` - generovanie stack-based instrukcii
- `interpreter.py` - vykonavanie vygenerovanych instrukcii

## Zakladne prikazy

### 1. Regenerovanie parsera po zmene gramatiky

```powershell
py -3.13 generate_parser.py
```

### 2. Kompilacia source programu do instrukcii

```powershell
py -3.13 main.py compile program.pjp -o output.txt
```

### 3. Spustenie uz vygenerovanych instrukcii

```powershell
py -3.13 main.py run output.txt
```

### 4. Spustenie instrukcii so vstupom zo suboru

```powershell
py -3.13 main.py run output.txt --input input.txt
```

### 5. Kompilacia a spustenie naraz

```powershell
py -3.13 main.py execute program.pjp
```

### 6. Kompilacia a spustenie so vstupom zo suboru

```powershell
py -3.13 main.py execute program.pjp --input input.txt
```

## Poznamky

- Po kazdej zmene `PJP.g4` treba znova spustit `py -3.13 generate_parser.py`.
- `run` spusta len instrukcny subor, nie source program.
- `execute` je najjednoduchsi command na bezne testovanie.
- Ak program pouziva `read` a nedas `--input`, hodnoty sa zadavaju rucne v konzole.
- Instruction-based format so samostatnym `open` a `fwrite 2` zatial nie je implementovany.
