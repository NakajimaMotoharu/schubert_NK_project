"""Add source and result references for ten newly executed tool-only tests."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
ARCH = Path('tools/quality/architecture/ModuleDependencyAudit.java')
PROBE = Path('tools/quality/jacoco_readonly_exec_subset.py')


def ref(path):
    return dict(path=str(path), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def read(path):
    return json.loads(Path(path).read_bytes())


def git(*args):
    return subprocess.check_output(['git', *args], timeout=15)


def main():
    start = read(next(D.glob('632_G08*.json')))['values']
    head = git('rev-parse', 'HEAD').decode().strip()
    assert head == start['source']
    x, y = start['oracleReferences']
    assert ref(x['path']) == x and ref(y['path']) == y
    arch, probe = read(x['path']), read(y['path'])
    assert arch['productionCore'] == probe['productionCore'] == start['productionCoreMain']
    arch_after, probe_after = arch['phases'][-1], probe['evidence'][-1]
    assert ref(arch_after['path']) == arch_after and ref(probe_after['path']) == probe_after
    a, b = read(arch_after['path']), read(probe_after['path'])
    assert a['source'] == arch['source'] and b['source'] == probe['source']
    assert hashlib.sha256(git('show', f"{head}:{ARCH}")).hexdigest() == a['toolSha256']
    assert ref(PROBE) == b['tools'][0]
    assert a['matched'] == 4 and b['actualExit'] == 0 and set(b['outcomes'].values()) == {'ok'}
    arch_rows = [dict(testId=c['testId'], design='SS311 §5.2', owner='WBS-F02',
                      target=c['origin']+' → '+c['target'], source=a['source'], proof=arch_after)
                 for c in a['cases']]
    probe_rows = [dict(testId=id_, design='SS354', owner='WBS-P018-08.03',
                       target=method, source=b['source'], proof=probe_after)
                  for id_, method in b['tests'].items()]
    assert {r['testId'] for r in arch_rows} == {f'PT-F02-ARCH-{n:03}' for n in range(23, 27)}
    assert {r['testId'] for r in probe_rows} == {f'PT-P01808-BIN-{n:03}' for n in range(18, 24)}
    assert len(arch_rows + probe_rows) == 10
    result = dict(actualExit=0, source=head, productionCore=start['productionCoreMain'],
                  toolRows=arch_rows + probe_rows, evidence=[x, y], newExecutions=0, newFormalIntake=0,
                  wholeG08Accepted=False, terminalAtUTC=datetime.now(timezone.utc).isoformat())
    folder = E / start['run']
    folder.mkdir()
    path = folder / 'manifest.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(ref(path))


if __name__ == '__main__':
    main()
