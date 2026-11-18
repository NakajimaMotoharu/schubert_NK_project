"""Cross-check saved tool exits, fixture bytes, and independent SS311 edge expectations."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
RUNS = ('PG40142-f02-controller-spring-jdbc-before-v1', 'PG40144-f02-controller-spring-jdbc-after-v1')
PREFIX = 'dev.codex.schubert.nk.web.canary.'
TOOL = 'tools/quality/architecture/ModuleDependencyAudit.java'
EXPECTED = {
    'PT-F02-ARCH-023': ('JdbcTemplateController', 'org.springframework.jdbc.core.JdbcTemplate', True),
    'PT-F02-ARCH-024': ('JdbcOperationsEndpoint', 'org.springframework.jdbc.core.JdbcOperations', True),
    'PT-F02-ARCH-025': ('TechnicalReadFacade', 'org.springframework.jdbc.core.JdbcTemplate', False),
    'PT-F02-ARCH-026': ('ReadFacadeController', PREFIX + 'TechnicalReadFacade', False),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(Path(path).read_bytes()))


def git(*args):
    return subprocess.check_output(['git', *args], timeout=20)


def main():
    pins = [ref(E / run / 'manifest.json') for run in RUNS]
    before, after = (json.loads(Path(pin['path']).read_bytes()) for pin in pins)
    assert before['source'] != after['source'] == git('rev-parse', 'HEAD').decode().strip()
    assert before['currentCore'] == after['currentCore']
    assert before['physical'] == after['physical']
    assert len(after['physical']) == 6 and sum(map(len, after['physical'].values())) == 10
    assert not git('diff', '--name-only', before['source'], after['source'], '--', 'src')
    for phase, run, expected in ((before, RUNS[0], False), (after, RUNS[1], True)):
        assert phase['toolSha256'] == sha(git('show', f"{phase['source']}:{TOOL}"))
        assert phase['receipts']['audit']['actualExit'] == int(expected)
        for name, result in phase['receipts'].items():
            assert json.loads((E / run / (name + '-exit.json')).read_bytes()) == result
            for key in ('stdout', 'stderr'):
                assert ref(result[key]['path']) == result[key]
        assert len(phase['cases']) == 4
        by_id = {row['testId']: row for row in phase['cases']}
        assert by_id.keys() == EXPECTED.keys()
        for id_, (origin, target, forbidden) in EXPECTED.items():
            row = by_id[id_]
            assert (row['origin'], row['target'], row['expected']) == (PREFIX + origin, target, forbidden)
            assert row['observed'] is (forbidden and expected)
        actual = (E / run / 'audit.stdout.txt').read_text().splitlines()
        hits = [line.split('\t')[1:] for line in actual if line.startswith('FINDING\t')]
        assert set(map(tuple, hits)) == {('CONTROLLER_BOUNDARY', PREFIX + origin, target)
                                         for origin, target, forbidden in EXPECTED.values() if forbidden and expected}
    assert before['matched'] == 2 and after['matched'] == 4
    result = dict(actualExit=0, source=after['source'], productionCore=after['currentCore'], phases=pins,
                  tests=list(EXPECTED), beforeMatched=2, afterMatched=4, syntheticPhysical=10,
                  productTests=0, productJars=0, formalIntake=0, wholeF02Accepted=False,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = E / 'PG40146-f02-controller-spring-jdbc-independent-v1'
    out.mkdir()
    p = out / 'manifest.json'
    p.write_text(json.dumps(result, indent=2) + '\n')
    print(ref(p))


if __name__ == '__main__':
    main()
