"""Independent readback-limit/SQL-call guard. Operator-only, Production PT0."""
import ast
from pathlib import Path

source = ast.parse(Path(__file__).with_name('pg500_restart_readonly_v1.py').read_text())
payload = next(n.value.value for n in source.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'payload' for t in n.targets))
parsed = ast.parse(payload)
command = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == 'command')
class Result:
    def __init__(self, code, size):
        self.returncode, self.stdout = code, bytearray(size)
class Calls:
    DEVNULL, PIPE = -3, -1
    def __init__(self, code, size):
        self.result = Result(code, size)
    def run(self, *args, **kwargs):
        return self.result
checks = 0
for code, size, expected in [(0, 0, True), (0, 8*1024*1024+1, True),
                             (0, 21337529, True), (0, 32*1024*1024, True),
                             (0, 32*1024*1024+1, False), (1, 1, False)]:
    env = {'subprocess': Calls(code, size)}
    exec(compile(ast.Module(body=[command], type_ignores=[]), 'fixed command guard', 'exec'), env)
    try:
        env['command'](['literal-readonly'], 33554432)
        actual = True
    except AssertionError:
        actual = False
    assert actual == expected
    checks += 1
database = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == 'database')
calls = [n for n in ast.walk(database) if isinstance(n, ast.Call)
         and isinstance(n.func, ast.Name) and n.func.id == 'command']
assert len(calls) == 1 and len(calls[0].args) == 2
assert eval(compile(ast.Expression(calls[0].args[1]), 'literal bound', 'eval'), {'__builtins__': {}}) == 33554432
assert 'repeatable read read only' in payload and 'assert result==tables' in payload
print('PG500_READONLY_ORACLE independentAssertions=' + str(checks + 3) + ' productionPT0=true')
