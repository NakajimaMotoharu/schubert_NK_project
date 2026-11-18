"""Cross-check the stored order DAG using a separately transcribed graph."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
RESULT = next(E.glob('PG40094-c02-current-unit-text-order-v1/manifest.json'))
EXPECTED = {
    'postgresql': set(),
    'backup': {'postgresql'},
    'admin': {'postgresql'},
    'cleanup': {'postgresql', 'backup'},
    'inspector': {'postgresql'},
    'artemis': {'cleanup', 'inspector'},
    'expiry': {'postgresql', 'artemis'},
    'api': {'postgresql', 'artemis', 'expiry', 'backup', 'cleanup', 'inspector'},
    'web': {'api', 'postgresql', 'artemis', 'backup', 'cleanup', 'expiry', 'inspector'},
    'caddy': {'backup', 'cleanup', 'expiry', 'inspector'},
    'morning': {'postgresql'},
    'target': {'morning'},
}
EXPECTED_TESTS = {
    'PT-C02-TEXT-002': 'TYPE_TIME_EXIT_POLICY',
    'PT-C02-TEXT-003': 'TYPE_TIME_EXIT_POLICY',
    'PT-C02-TEXT-004': 'SIGKILL_POLICY',
    'PT-C02-TEXT-005': 'NO_PARALLEL_CHILD_ACTIVATION',
    'PT-C02-TEXT-006': 'SIGNED_REQUIRES',
    'PT-C02-TEXT-007': 'ORDER_CYCLE',
    'PT-C02-TEXT-008': 'REPEATED_DIRECTIVE',
    'PT-C02-TEXT-009': 'STOP_ONLY',
}


def reference(path):
    return dict(path=str(path), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def alias(name):
    names = {'inbox-inspector': 'inspector', 'bootstrap-admin': 'admin',
             'expiry-cleanup': 'expiry', 'morning-controller': 'morning'}
    name = name.removesuffix('.template')
    if name == 'schubert-nk-morning.target':
        return 'target'
    name = name.removesuffix('.service').removeprefix('schubert-nk-')
    return names.get(name, name)


def main():
    source = json.loads(RESULT.read_text())
    assert source['actualExit'] == 0 and source['sourceOnly'] and not source['returnedUnitEvidence']
    assert len(source['currentFiles']) == 14
    graph = {key: set() for key in EXPECTED}
    for row in source['currentFiles']:
        path = Path(row['path'])
        assert reference(path)['sha256'] == row['sha256']
        raw = subprocess.check_output(['git', 'show', f'{row["source"]}:{path}'], timeout=20)
        assert hashlib.sha256(raw).hexdigest() == row['sha256']
        if path.suffix == '.conf':
            continue
        current = alias(path.name)
        for line in raw.decode().splitlines():
            key, _, value = line.partition('=')
            if key == 'After':
                graph[current].update(map(alias, value.split()))
            if key == 'Before':
                for successor in map(alias, value.split()):
                    graph[successor].add(current)
    assert graph == EXPECTED
    assert sum(map(len, graph.values())) == source['fixedOrderEdges'] == 28
    non_root_keys = {unit for unit, dependencies in graph.items() if dependencies}
    assert len(non_root_keys) == source['graphNodes'] == 11 and len(graph) == 12
    got = {row['testId']: row['actual'] for row in source['tests'][1:] if row['passed']}
    assert got == EXPECTED_TESTS
    assert source['tests'][0]['testId'] == 'PT-C02-TEXT-001' and source['tests'][0]['passed']
    actual = subprocess.check_output(
        ['git', 'show', f'{source["canonical"]["source"]}:{source["canonical"]["path"]}'], timeout=20
    ).decode()
    assert '\x60caddy\x60 | Web | Web' in actual
    assert 'Caddy package実Unit' in actual
    value = dict(actualExit=0, proof=reference(RESULT), sourceCore=source['sourceCore'],
        files=14, nodes=len(graph), edges=source['fixedOrderEdges'], independentNegativeIDs=EXPECTED_TESTS,
        tests=9, productTests=0, realHostOperations=0, wholeC02Accepted=False,
        initialIndependentPreparationExits=[1, 1],
        initialIndependentIssues=['Strip .template before assigning target shorthand',
                                  'Primary stored graph key count excludes predecessor-only PostgreSQL'],
        declaredTargetKeyCount=source['graphNodes'], completeGraphVertexCount=len(graph),
        pending=['current effective Caddy ordering', 'current boot and Inspector terminal',
                 'native owned postcondition', 'formal 451'],
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), verifier=reference(__file__))
    path = RESULT.parent / 'independent.json'
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(reference(path))


if __name__ == '__main__':
    main()
