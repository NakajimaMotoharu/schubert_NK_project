"""Bind the approved current style denominator to the three new view tests."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess


PMO = Path('documents/400_PGPT/470_PMO')
OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')


def pin(path):
    return dict(path=str(path),sha256=sha256(path.read_bytes()).hexdigest())


def git(*args):
    return subprocess.check_output(['git',*args],timeout=20).decode()


def main():
    start, = PMO.glob('601_*/1610_*.json')
    context = json.loads(start.read_bytes())['values']
    assert all(pin(Path(ref['path']))==ref for ref in context['oracleReferences'])
    prior, *evidence = [Path(ref['path']) for ref in context['oracleReferences'][1:]]
    old = json.loads(prior.read_bytes())
    assert old['actualExit']==0 and old['productionCore']==context['productionCoreMain']
    head = context['source']
    assert git('rev-parse','HEAD').strip()==head
    assert not git('diff','--name-only',old['source'],head,'--', ':(glob)src/**/src/main/**')
    names = git('diff','--name-status','-z',old['source'],head,'--','src').split('\0')[:-1]
    assert names[::2]==['A','A','A']
    new_cases = []
    for receipt in evidence:
        data = json.loads(receipt.read_bytes())
        assert data['actualExit']==0 and data['productionCore']==context['productionCoreMain']
        case = data['testSource']
        fresh = subprocess.check_output(['git','show',f'{head}:{case["path"]}'],timeout=20)
        assert pin(Path(case['path']))==case and sha256(fresh).hexdigest()==case['sha256']
        fmt = data['stages']['format']
        style = data['stages']['checkstyle'] if 'checkstyle' in data['stages'] else data['stages']['style']
        assert fmt['exit']==style['exit']==0
        assert '--dry-run' in fmt['command'] and fmt['command'][-1]==case['path']
        assert style['command'][-1]==case['path']
        new_cases.append(dict(testId=data['testId'],testSource=case,originalStage=pin(receipt),
                              formatExit=fmt['exit'],checkstyleExit=style['exit']))
    assert {entry['testSource']['path'] for entry in new_cases}==set(names[1::2])
    tracked = git('ls-tree','-r','--name-only',head,'--','src').splitlines()
    main = sum('/src/main/java/' in name and name.endswith('.java') for name in tracked)
    tests = sum('/src/test/java/' in name and name.endswith('.java') for name in tracked)
    previous = old['sourceTotals']
    updated = dict(main=main,tests=tests,checkedTests=previous['testCheckstyleConfirmed']+len(new_cases),
                   heldTests=previous['heldTests'])
    assert main==previous['main']==1027 and tests==previous['tests']+len(new_cases)
    assert updated['checkedTests']+updated['heldTests']==tests
    output = OPS/'PG41184-f03-static-three-view-test-delta-v1'
    output.mkdir()
    target = output/'manifest.json'
    with target.open('x') as stream:
        json.dump(dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                       source=head,productionCore=context['productionCoreMain'],previous=pin(prior),
                       current=updated,added=new_cases,staticReplayed=0,productTestReplayed=0,
                       heldBytesOpened=0,wholeF03=False,whole451=False,formalDelta=0),
                  stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(pin(target),updated)


if __name__=='__main__':
    main()
