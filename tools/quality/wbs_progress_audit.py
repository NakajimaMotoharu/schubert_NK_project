"""Read-only WBS/snapshot reconciliation. Never qualifies Production PG/PT."""
import collections
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PMO = ROOT / 'documents/400_PGPT/470_PMO'


def classify(counters):
    if not counters:
        return 'NO_HOST_MEASUREMENT'
    if any(item is None for item in counters):
        return 'TARGET_ABSENT'
    if all(item[5] > 0 and all(item[i] == 0 for i in (0, 2, 4, 6))
           for item in counters):
        return 'HOST_COUNTERS_CLOSED'
    return 'HOST_GAPS'


def verify():
    master = json.loads((PMO / '481_PGPT詳細WBS.json').read_text())
    snapshot = json.loads((PMO / '482_WBS実績snapshot_20261007.json').read_text())
    ids = [t['id'] for t in master['tasks']]
    assert len(ids) == len(set(ids)), 'duplicate WBS ID'
    assert len(ids) == snapshot['allTasks'] == 190
    assert len(master['programs']) == 20
    assert len([t for t in master['tasks'] if t['kind'] == 'CHR']) == 24
    assert {t['program'] for t in master['tasks']} == {p['program'] for p in master['programs']}
    states = {r['id']: r for r in snapshot['rows']}
    assert set(states) == set(ids)
    graph = {t['id']: t['dependencies'] for t in master['tasks']}
    finished = set()

    def visit(node, active):
        assert node not in active, 'dependency cycle'
        if node in finished:
            return
        for dependency in graph[node]:
            visit(dependency, active | {node})
        finished.add(node)

    for node in graph:
        visit(node, set())
    for task in master['tasks']:
        assert all(dep in ids for dep in task['dependencies']), task['id']
        assert task['deliverables'] and task['exitCriteria'] and task['ss']
        row = states[task['id']]
        if task['kind'] == 'COMPONENT':
            counters = [[t['missed']['LINE'], 0, t['missed']['METHOD'], 0,
                         t['missed']['CLASS'], t['coveredClassCount'],
                         t['missed']['BRANCH'], 0] for t in row['targets']]
            assert classify(counters) == row['currentStatus'], task['id']
            assert classify([t['baselineCounter'] for t in row['targets']]) == row['baselineStatus']
        for evidence in row['evidence']:
            assert (ROOT / evidence).exists(), evidence
    counts = dict(collections.Counter(r['currentStatus'] for r in states.values()))
    assert counts == snapshot['counts']
    component = [r for r in states.values() if r['kind'] == 'COMPONENT']
    closed = {r['id'] for r in component if r['currentStatus'] == 'HOST_COUNTERS_CLOSED'}
    old = {r['id'] for r in component if r['baselineStatus'] == 'HOST_COUNTERS_CLOSED'}
    assert closed - old == set(snapshot['componentDelta']['newlyCounterClosed'])
    assert old - closed == set(snapshot['componentDelta']['reopened'])
    assert snapshot['wholeEffortCompletionRate'] is None
    assert snapshot['formal']['deltaTests'] == snapshot['formal']['deltaScopes'] == 0
    # Negative canaries: no targets, null, missing branches, and untouched class.
    assert classify([]) == 'NO_HOST_MEASUREMENT'
    assert classify([None]) == 'TARGET_ABSENT'
    assert classify([[0, 1, 0, 1, 0, 1, 1, 1]]) == 'HOST_GAPS'
    assert classify([[0] * 8]) == 'HOST_GAPS'
    assert classify([[0, 1, 0, 1, 0, 1, 0, 1]]) == 'HOST_COUNTERS_CLOSED'
    return {'wbsItems': len(ids), 'componentItems': len(component),
            'baselineCounterClosed': len(old), 'currentCounterClosed': len(closed),
            'newlyCounterClosed': len(closed - old), 'reopened': len(old - closed),
            'netCounterClosed': len(closed) - len(old), 'statusCounts': counts,
            'scopeAuditStillPending': 'WBS-G13', 'formalAcceptanceChanged': False,
            'businessImplementationChanged': False}


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
