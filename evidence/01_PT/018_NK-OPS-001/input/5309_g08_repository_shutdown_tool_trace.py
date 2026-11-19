"""Bind two existing tool-run proofs to exact WBS rows without executing either tool."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
ARCH = 'tools/quality/architecture/ModuleDependencyAudit.java'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_pin(pin):
    data = Path(pin['path']).read_bytes()
    assert sha(data) == pin['sha256']
    return json.loads(data)


def git(*args):
    return subprocess.check_output(['git', *args], timeout=20)


def main():
    start = json.loads(next(D.glob('654_G08*')).read_bytes())['values']
    head = git('rev-parse', 'HEAD').decode().strip()
    assert head == start['source']
    pins = start['oracleReferences']
    arch, unit, timeout = [read_pin(pin) for pin in pins]
    core = start['productionCoreMain']
    assert arch['productionCore'] == unit['productionCore'] == timeout['productionCore'] == core
    assert arch['afterMatched'] == 4 and unit['afterMatched'] == 6
    assert arch['productJars'] == arch['productTests'] == unit['actualEffectiveUnits'] == 0
    assert not arch['wholeF02Accepted'] and not unit['wholeC02Accepted']
    requalified_arch, requalified_unit = arch['artifacts'][-1], unit['candidates'][-1]
    a, b = read_pin(requalified_arch), read_pin(requalified_unit)
    assert a['source'] == arch['source'] and b['source'] == unit['source']
    assert sha(git('show', f'{head}:{ARCH}')) == a['toolSha256']
    assert sha(git('show', f"{head}:{b['gate']['path']}")) == b['gate']['sha256']
    assert a['tests'] == arch['tests'] and b['results'] == unit['outcomes']

    rows = []
    for test in arch['tests']:
        assert test['observed'] == test['expected']
        rows.append(dict(testId=test['testId'], activity='WBS-F02-a', design='SS311 §3', source=arch['source'],
                         evidence=requalified_arch, scope='SYNTHETIC_ARCHITECTURE',
                         condition=test['origin'] + ' → ' + test['target']))
    for test in unit['outcomes']:
        assert test['actual'] == test['expected']
        rows.append(dict(testId=test['testId'], activity='WBS-C02-a', design='SS341/342', source=unit['source'],
                         evidence=requalified_unit, scope='SOURCE_TEMPLATE_ONLY',
                         expectedRejection=test['expected']))
    assert {r['testId'] for r in rows} == ({f'PT-F02-ARCH-{i:03}' for i in range(27, 31)}
                                          | {f'PT-C02-TEXT-{i:03}' for i in range(10, 16)})
    assert len(rows) == 10
    assert timeout['priorTestsReused'] == 1 and timeout['priorTestsReexecuted'] == 0
    assert len(timeout['timeoutRows']) == 4
    assert all(r['effectiveObserved'] is None for r in timeout['timeoutRows'])
    evidence = dict(actualExit=0, source=head, productionCore=core, references=pins, toolRows=rows,
                    priorTimeoutReused=dict(testId='PT-C02-TEXT-001', conditions=4, proof=pins[-1]),
                    newProductTests=0, existingTestsReexecuted=0, newFormalAcceptance=0,
                    wholeG08Accepted=False, terminalAtUTC=datetime.now(timezone.utc).isoformat())
    folder = E / start['run']
    folder.mkdir()
    p = folder / 'manifest.json'
    p.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(sha(p.read_bytes()))


if __name__ == '__main__':
    main()
