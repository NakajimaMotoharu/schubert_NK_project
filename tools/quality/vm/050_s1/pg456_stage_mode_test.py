"""Independent literal modes against the actual embedded privileged placement function."""
import ast
import pathlib
import subprocess

tree = ast.parse(pathlib.Path(__file__).with_name('pg456_stage_candidate.py').read_text())
payload = next(n.value.value for n in tree.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'payload' for t in n.targets))
function = next(n for n in ast.parse(payload).body if isinstance(n, ast.FunctionDef) and n.name == 'payload_mode')
namespace = {}
exec(compile(ast.Module(body=[function], type_ignores=[]), '<actual-stage-function>', 'exec'), namespace)
mode = namespace['payload_mode']
vectors = [('operations/bin/schubert-nkctl', False, 0o750),
           ('operations/bin/schubert-nk-inbox-inspector', False, 0o750),
           ('operations/bin/unknown', False, 0o640),
           ('api/api.jar', False, 0o640), ('operations/bin', True, 0o750),
           ('other/operations/bin/schubert-nkctl', False, 0o640),
           ('/operations/bin/schubert-nkctl', False, 0o640)]
for path, directory, expected in vectors:
    assert mode(path, directory) == expected
# BUG664: guard failure must terminate BEFORE the observable downstream marker.
guard = subprocess.run(['bash', '-c', 'set -eu; (exit 7); printf SIDE_EFFECT'], capture_output=True)
assert guard.returncode == 7 and guard.stdout == b''
print('PG456_MODE_GUARD_PASS vectors7=true guardExit7=true downstreamSideEffects0=true productionPt0=true')
