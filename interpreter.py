from __future__ import annotations

import ast
import re


class Interpreter:
    INT_PATTERN = re.compile(r"^[+-]?[0-9]+$")
    FLOAT_PATTERN = re.compile(r"^[+-]?[0-9]+\.[0-9]+$")

    def __init__(self, filename: str, input_file: str | None = None) -> None:
        with open(filename, "r", encoding="utf-8") as handle:
            self.instructions = [line.strip() for line in handle if line.strip()]

        self.stack: list[object] = []
        self.memory: dict[str, object] = {}
        self.files: dict[str,object] = {}
        self.labels: dict[str, int] = {}
        self.ip = 0

        self.input_lines: list[str] | None = None
        self.input_index = 0
        if input_file is not None:
            with open(input_file, "r", encoding="utf-8") as handle:
                self.input_lines = [line.rstrip("\r\n") for line in handle]

        for index, line in enumerate(self.instructions):
            parts = line.split(maxsplit=1)
            if parts[0] == "label":
                self.labels[parts[1]] = index

    def read_value(self, value_type: str) -> object:
        if self.input_lines is None:
            raw_value = input().strip()
        else:
            if self.input_index >= len(self.input_lines):
                raise EOFError("Not enough input values for read instruction")
            raw_value = self.input_lines[self.input_index]
            self.input_index += 1

        if value_type == "I":
            if not self.INT_PATTERN.fullmatch(raw_value):
                raise ValueError(f"Invalid int input: {raw_value}")
            return int(raw_value)
        if value_type == "F":
            if not self.FLOAT_PATTERN.fullmatch(raw_value):
                raise ValueError(f"Invalid float input: {raw_value}")
            return float(raw_value)
        if value_type == "B":
            if raw_value not in {"true", "false"}:
                raise ValueError(f"Invalid bool input: {raw_value}")
            return raw_value == "true"
        if value_type == "S":
            return raw_value
        raise ValueError(f"Unknown input type: {value_type}")

    @staticmethod
    def format_value(value: object) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def run(self) -> None:
        try:
            while self.ip < len(self.instructions):
                line = self.instructions[self.ip]
                parts = line.split()
                command = parts[0]

                if command == "push":
                    value_type = parts[1]
                    raw_value = line.split(maxsplit=2)[2]
                    if value_type == "I":
                        self.stack.append(int(raw_value))
                    elif value_type == "F":
                        self.stack.append(float(raw_value))
                    elif value_type == "B":
                        self.stack.append(raw_value == "true")
                    elif value_type == "S":
                        self.stack.append(ast.literal_eval(raw_value))

                elif command == "pop":
                    self.stack.pop()

                elif command == "load":
                    self.stack.append(self.memory[parts[1]])

                elif command == "save":
                    self.memory[parts[1]] = self.stack.pop()

                elif command in {"add", "sub", "mul", "div"}:
                    value_type = parts[1]
                    right = self.stack.pop()
                    left = self.stack.pop()
                    if command == "add":
                        self.stack.append(left + right)
                    elif command == "sub":
                        self.stack.append(left - right)
                    elif command == "mul":
                        self.stack.append(left * right)
                    elif command == "div":
                        self.stack.append(int(left / right) if value_type == "I" else left / right)

                elif command == "mod":
                    right = self.stack.pop()
                    left = self.stack.pop()
                    self.stack.append(left % right)

                elif command == "uminus":
                    self.stack.append(-self.stack.pop())

                elif command == "itof":
                    self.stack.append(float(self.stack.pop()))

                elif command == "concat":
                    right = self.stack.pop()
                    left = self.stack.pop()
                    self.stack.append(str(left) + str(right))

                elif command == "and":
                    right = self.stack.pop()
                    left = self.stack.pop()
                    self.stack.append(left and right)

                elif command == "or":
                    right = self.stack.pop()
                    left = self.stack.pop()
                    self.stack.append(left or right)

                elif command == "not":
                    self.stack.append(not self.stack.pop())

                elif command == "gt":
                    right = self.stack.pop()
                    left = self.stack.pop()
                    self.stack.append(left > right)

                elif command == "lt":
                    right = self.stack.pop()
                    left = self.stack.pop()
                    self.stack.append(left < right)

                elif command == "eq":
                    right = self.stack.pop()
                    left = self.stack.pop()
                    self.stack.append(left == right)

                elif command == "label":
                    pass

                elif command == "jmp":
                    self.ip = self.labels[parts[1]]
                    continue

                elif command == "fjmp":
                    condition = self.stack.pop()
                    if not condition:
                        self.ip = self.labels[parts[1]]
                        continue

                elif command == "print":
                    count = int(parts[1])
                    values = self.stack[-count:]
                    del self.stack[-count:]
                    print("".join(self.format_value(value) for value in values))

                elif command == "read":
                    self.stack.append(self.read_value(parts[1]))

                elif command == "fopen":
                    file_name = parts[1]
                    raw_path = line.split(maxsplit=2)[2]
                    path = ast.literal_eval(raw_path)
                    self.files[file_name] = open(path, "w", encoding="utf-8")

                elif command == "fwrite":
                    file_name = parts[1]

                    if file_name not in self.files:
                        raise ValueError(f"File variable '{file_name} is not opened")
                    value = self.stack.pop()
                    self.files[file_name].write(self.format_value(value))
                    
                else:
                    raise ValueError(f"Unknown instruction: {line}")

                self.ip += 1
                
        finally:
            for handle in self.files.values():
                handle.close()
