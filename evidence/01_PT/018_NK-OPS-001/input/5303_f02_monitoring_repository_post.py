"""Cross-check fixed repository dependency outcomes against original audit bytes."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
NAMES = ('PG40170-f02-monitoring-repository-before-v1', 'PG40172-f02-monitoring-repository-after-v1')
OUT = E / 'PG40174-f02-monitoring-repository-independent-v1'
API = 'dev.codex.schubert.nk.api.'
APP = API + 'application.log.DummyService'
DENIED = (API + 'persistence.DummyRepository', API + 'monitoring.persistence.MonitoringRepository')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return {'path': str(path), 'sha256': sha(Path(path).read_bytes())}


def main():
    values = []
    refs = []
    for idx, folder in enumerate(NAMES):
        p = E / folder / 'manifest.json'
        row = json.loads(p.read_bytes())
        refs.append(ref(p))
        values.append(row)
        tool = subprocess.check_output(['git', 'show', f"{row['source']}:tools/quality/architecture/ModuleDependencyAudit.java"])
        assert sha(tool) == row['toolSha256']
        assert all(ref(s['stdout']['path']) == s['stdout'] and ref(s['stderr']['path']) == s['stderr']
                   for s in row['receipts'].values())
        assert [row['receipts'][name]['actualExit'] for name in ('tool-compile', 'fixture-compile', 'audit')] == [0, 0, 1]
        report = Path(row['receipts']['audit']['stdout']['path']).read_text().splitlines()
        assert {line for line in report if line.startswith('FINDING\t')} == {
            f'FINDING\tREPOSITORY_DIRECTION\t{origin}\t{APP}' for origin in DENIED[:idx + 1]}
        assert [(r['testId'], r['expected'], r['observed']) for r in row['tests']] == [
            ('PT-F02-ARCH-027', True, True), ('PT-F02-ARCH-028', True, bool(idx)),
            ('PT-F02-ARCH-029', False, False), ('PT-F02-ARCH-030', False, False)]
    old, fixed = values
    assert old['matched'] == 3 and fixed['matched'] == 4 and old['core'] == fixed['core']
    assert old['physical'] == fixed['physical'] and len(fixed['physical']) == 6
    assert sum(len(classes) for classes in fixed['physical'].values()) == 10
    assert not subprocess.check_output(['git', 'diff', '--name-only', old['source'], fixed['source'], '--', 'src'])
    OUT.mkdir()
    p = OUT / 'manifest.json'
    result = dict(actualExit=0, source=fixed['source'], productionCore=fixed['core'], artifacts=refs,
                  tests=fixed['tests'], beforeMatched=3, afterMatched=4, wholeF02Accepted=False,
                  productTests=0, productJars=0, newFormalAcceptance=0,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    p.write_text(json.dumps(result, indent=2) + '\n')
    print(ref(p))


if __name__ == '__main__':
    main()
