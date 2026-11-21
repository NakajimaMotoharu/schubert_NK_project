"""Run one normal full Protocol verify on the committed BUG-3494 candidate."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from tempfile import mkdtemp

ROOT = Path.cwd()
OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PLAN = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
RUN = 'PG41526-protocol-qa054-canonical-rules-v1'
MODULE = Path('src/schubert-nk-protocol')


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return {'path': str(path), 'sha256': sha(path.read_bytes())}


def read(path):
    return json.loads(path.read_bytes())


def write(path, data):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def git(*args):
    return subprocess.check_output(['git', *args], timeout=30)


def main():
    checkpoint = read(next(PLAN.glob('1927_*')))
    source = checkpoint['source']
    q = checkpoint['quotaObservation']
    age = datetime.now(timezone.utc) - datetime.fromisoformat(q['observedAtUTC'])
    assert 0 <= age.total_seconds() <= 120 and q['ordinaryUsageAllowed']
    assert all(v is None or v['remainingPercent'] > 10 for v in (q['primary'],q['secondary']))
    assert source == git('rev-parse', 'HEAD').decode().strip()
    prior_dir = OPS / 'PG41302-protocol-numeric-full-maven-v1'
    prior = read(prior_dir/'begin.json')
    assert pin(Path(prior['input']['path'])) == prior['input']
    assert read(prior_dir/'terminal.json')['actualExit'] == 0
    inputs = read(Path(prior['input']['path']))
    assert len(inputs) == 217
    current = {name: git('show', f'{source}:{name}') for name in inputs}
    changed = [p for p, data in current.items() if sha(data) != inputs[p]['sha256']]
    exact_change = {
        str(MODULE/'src/main/java/dev/codex/schubert/nk/protocol/layout/LayoutFieldCatalog.java'),
        str(MODULE/'src/test/resources/protocol/fields-ui234-236.tsv'),
    }
    assert set(changed) == exact_change
    tree = set(git('ls-tree','-r','--name-only',source,'--',str(MODULE)).decode().splitlines())
    assert tree == {p for p in inputs if p.startswith(str(MODULE)+'/')}
    java = Path(prior['java']['path'])
    maven = Path(prior['maven']['path'])
    assert pin(java) == prior['java'] and pin(maven) == prior['maven']
    work=Path(mkdtemp(prefix='pgpt-qa054-protocol-current-',dir='/dev/shm'))
    for name, content in current.items():
        p = work/name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(content)
    command = list(prior['command'])
    assert command[-1]=='verify' and command[0]==str(maven) and '-o' in command
    command[-2] = str(work/MODULE/'pom.xml')
    home = ROOT.parent/'pgpt-runs/PG379'/RUN
    home.mkdir(mode=0o700)
    receipt = dict(run=RUN, source=source, scope='Protocol only', expectedTests=171, expectedSuites=39,
                   originMain=git('rev-parse','origin/main').decode().strip(), work=str(work), argv=command,
                   currentInputs={p:sha(v) for p,v in current.items()}, twoInputDeltas=changed,
                   oldUnitStart=pin(prior_dir/'begin.json'), java=pin(java),maven=pin(maven),startUTC=now())
    write(home/'begin.json',receipt)
    tool_environment = {**os.environ,'JAVA_HOME':str(java.parent.parent),'LC_ALL':'C.UTF-8','TZ':'Asia/Tokyo'}
    with (home/'maven.log').open('xb') as log:
        result = subprocess.run(command,cwd=work,env=tool_environment,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    results = sorted((work/MODULE/'target/surefire-reports').glob('TEST-*.xml'))
    write(home/'terminal.json',dict(run=RUN,source=source,exitCode=result.returncode,receipt=pin(home/'begin.json'),
         log=pin(home/'maven.log'),reportCount=len(results),terminalAtUTC=now()))
    print('Verify exit',result.returncode,'reports',len(results),'run',RUN)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
