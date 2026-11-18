"""Capture exact parser boundary outcomes against the pre-fix and corrected tool commits."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import platform
import re
import subprocess
import sys

BASE=Path('evidence/01_PT/018_NK-OPS-001/evidence')
DOC=Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117')
TOOLS=('tools/quality/jacoco_readonly_exec_subset.py','tools/quality/jacoco_readonly_exec_subset_test.py')
PHASE={'red':('PG40022-p01808-binary-session-signed-red-v1',1,4),
       'green':('PG40024-p01808-binary-session-signed-green-v1',0,0)}


def pin(path):
    return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def git(*args):
    return subprocess.check_output(['git',*args],timeout=15)


def main(phase):
    name, expected_exit, expected_fails=PHASE[phase]
    output=BASE/name
    start=json.loads(next(DOC.glob('557_*')).read_bytes())['values']
    source=git('rev-parse','HEAD').decode().strip()
    assert not git('diff','--name-only','HEAD','--',*TOOLS)
    assert all(Path(name).read_bytes()==git('show',f'{source}:{name}') for name in TOOLS)
    red=BASE/PHASE['red'][0]/'manifest.json'
    pins=[pin(Path(p)) for p in TOOLS]
    if phase=='red':
        assert pins[0]==start['oracleReferences'][2]
    else:
        first=json.loads(red.read_bytes())
        assert first['inputs'][1]==pins[1] and first['inputs'][0]!=pins[0] and first['actualExit']==1
    output.mkdir()
    args=[sys.executable,'-B','-m','unittest','discover','-s','tools/quality','-p',Path(TOOLS[1]).name,'-v']
    begin=datetime.now(timezone.utc).isoformat()
    result=subprocess.run(args,capture_output=True,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},timeout=30)
    log=output/'unittest-output.txt'
    with log.open('xb') as f:
        f.write(result.stdout+result.stderr)
    actual=log.read_text()
    assert 'Ran 9 tests' in actual
    if phase=='green':
        assert 'Traceback' not in actual
    errors=len(re.findall(r'^ERROR: ',actual,re.M))
    failed=re.findall(r'^FAIL: (\w+)',actual,re.M)
    assert result.returncode==expected_exit and errors==0 and len(failed)==expected_fails
    assert actual.rstrip().endswith('OK' if phase=='green' else 'FAILED (failures=4)')
    assert not re.search(r'\.\.\. (?:skipped|expected failure|unexpected success)',actual)
    receipt=dict(actualExit=result.returncode,source=source,productionCoreMain=start['productionCoreMain'],
        phase=phase,command=args,python=platform.python_version(),os=platform.platform(),run=name,
        inputs=pins,log=pin(log),harness=pin(Path(__file__)),firstVerificationDenominator=9,
        originalEmbeddedVectors=12,newVectors=8,namedTests=9,passed=9-len(failed),failures=len(failed),
        errors=errors,skipped=0,notRun=0,failedMethods=failed,productTests=0,actualCoverage=0,
        protectedOperations=0,earlierRed=pin(red) if phase=='green' else None,
        newAcceptance=0,whole451Accepted=False,startedAtUTC=begin,terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with (output/'manifest.json').open('x') as f:
        json.dump(receipt,f,indent=2)
        f.write('\n')
    print(receipt['actualExit'],receipt['passed'],receipt['failures'],pin(output/'manifest.json')['sha256'])
    return receipt['actualExit']


if __name__=='__main__':
    raise SystemExit(main(sys.argv[1]))
