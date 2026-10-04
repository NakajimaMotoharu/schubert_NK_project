"""BUG625/YKT442: bounded exact-class six-module selector preflight, never executes Maven."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[4]
if len(sys.argv) != 2 or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(,[A-Za-z_][A-Za-z0-9_]*)*', sys.argv[1]):
    print('SELECTOR_REJECTED exact class list required')
    raise SystemExit(2)
selected = set(sys.argv[1].split(','))
missing = []
for module in ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'):
    tests = root / f'src/schubert-nk-{module}/src/test/java'
    present = sorted(path.stem for path in tests.rglob('*.java') if path.stem in selected and path.stem.endswith('Test'))
    if not present:
        missing.append(module)
    print(module + ': ' + str(len(present)) + ' exact test classes')
if missing:
    print('SELECTOR_REJECTED missing modules=' + ','.join(missing))
    raise SystemExit(1)
print('SELECTOR_ACCEPTED six module canaries; actual XML and results still required')
