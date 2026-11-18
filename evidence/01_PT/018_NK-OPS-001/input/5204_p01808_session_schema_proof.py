"""Qualify the named session parser without opening or producing any current native stream."""
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd()
OUT = Path('evidence/01_PT/018_NK-OPS-001/evidence/PG39710-p01808-session-long-boundary-v1')
PARSER = Path('tools/quality/coverage_session_schema.py')
TEST = Path('tools/quality/coverage_session_schema_test.py')
START = Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117/483_P01808取得session数値境界開始.json')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return {'path': str(path), 'sha256': digest(path.read_bytes())}


def git(*args):
    return subprocess.check_output(['git', *args], timeout=30)


def now():
    return datetime.now(timezone.utc).isoformat()


def write(path, obj):
    with path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def run(name, arguments):
    command = [sys.executable, '-B', *arguments]
    started = now()
    result = subprocess.run(command, env={'PYTHONPATH': str(ROOT / 'tools/quality'),
                                        'LANG': 'C.UTF-8', 'TZ': 'Asia/Tokyo'},
                            cwd=ROOT, capture_output=True, timeout=20)
    end = now()
    files = {}
    for key, data in [('stdout', result.stdout), ('stderr', result.stderr)]:
        file = OUT / (name + '.' + key)
        with file.open('xb') as f:
            f.write(data)
        files[key] = ref(file)
    return dict(command=command, startedAtUTC=started, terminalAtUTC=end, actualExit=result.returncode, files=files)


def validate_callers(base, fixed):
    match = '(^from coverage_session_schema |^import coverage_session_schema)'
    files = git('grep', '-l', '-E', match, base, '--', ':(glob)tools/quality/**/*.py').decode().splitlines()
    assert len(files) == 96
    receipts = []
    totals = Counter()
    for result in files:
        path = result.split(':', 1)[1]
        text = git('show', f'{base}:{path}')
        assert text == git('show', f'{fixed}:{path}')
        module = ast.parse(text, filename=path)
        aliases = {
            value.asname or value.name: value.name for node in ast.walk(module)
            if isinstance(node, ast.ImportFrom) and node.module == 'coverage_session_schema'
            for value in node.names
        }
        assert aliases and set(aliases.values()) <= {'parse', 'selftest'}
        calls = []
        for node in ast.walk(module):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            function = aliases.get(node.func.id)
            if function is None:
                continue
            assert not node.keywords
            assert len(node.args) == (2 if function == 'parse' else 0)
            totals[function] += 1
            calls.append(dict(function=function, line=node.lineno, count=len(node.args)))
        assert calls
        receipts.append(dict(path=path, sha256=digest(text), unchangedFromPlan=True, parsedCalls=calls))
    assert totals == {'parse': 95, 'selftest': 95}
    write(OUT / 'public-call-shapes.json', receipts)
    return dict(files=len(receipts), parse=totals['parse'], selftest=totals['selftest'],
                importOrRunHistoricalTools=0, compileSourceOnly=True,
                exactFileList=ref(OUT / 'public-call-shapes.json'))


def main():
    requested = json.loads(START.read_bytes())
    before_path = OUT / 'raw-before.json'
    before = json.loads(before_path.read_bytes())
    fixed = git('rev-parse','HEAD').decode().strip()
    base = requested['values']['source']
    assert before['sourceBefore'] == base
    assert before['parserBeforeSha256'] == digest(git('show', f'{base}:{PARSER}'))
    assert len(before['originalFourWrongAcceptances']) == 4
    for item in (PARSER, TEST):
        assert git('show', f'{fixed}:{item}') == item.read_bytes()
    assert not git('diff','--name-only',base,fixed,'--','src')
    old = ast.parse(git('show', f'{base}:{PARSER}'))
    new = ast.parse(PARSER.read_bytes())
    old_test = next(a for a in old.body if isinstance(a,ast.FunctionDef) and a.name=='selftest')
    new_test = next(a for a in new.body if isinstance(a,ast.FunctionDef) and a.name=='selftest')
    assert ast.dump(old_test) == ast.dump(new_test)
    call = validate_callers(base, fixed)
    new_result = run('additional-seven', ['-m', 'unittest', '-v', 'coverage_session_schema_test'])
    original_result = run('original-seven', ['-c', 'from coverage_session_schema import selftest; assert selftest() == 7; print(7)'])
    assert new_result['actualExit'] == original_result['actualExit'] == 0
    stderr = Path(new_result['files']['stderr']['path']).read_text()
    assert 'Ran 7 tests' in stderr and stderr.rstrip().endswith('OK')
    for id in range(8, 15):
        assert stderr.count(f'test_{id:03}_') == 2
    assert Path(original_result['files']['stdout']['path']).read_bytes() == b'7\n'
    evidence = dict(actualExit=0, startEvent=requested['eventId'], terminalAtUTC=now(), source=fixed,
                    productionCoreMain=requested['values']['productionCoreMain'], parser=ref(PARSER),
                    toolTest=ref(TEST), historicalCallerValidation=call, originalFailure=ref(before_path),
                    javaAbi=ref(OUT/'jacoco-session-abi.txt'), toolPython=sys.version.split()[0],
                    originalToolVectors=7, addedToolTests=7, additionalFirstExecuted=7,
                    failed=0, errors=0, skipped=0, nativeStreamsOpened=0, productTests=0,
                    currentMeasuredProductCoverage=0, newAcceptance=0, whole451Accepted=False,
                    originalRuntimeOwnerNotQualified=True, executions=[original_result,new_result],
                    verifier=ref(Path(__file__).relative_to(ROOT)))
    p = OUT / 'manifest.json'
    write(p, evidence)
    print(ref(p))


if __name__ == '__main__':
    main()
