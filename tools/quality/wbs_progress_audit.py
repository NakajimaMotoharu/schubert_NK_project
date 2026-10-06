"""Read-only WBS/snapshot reconciliation. Never qualifies Production PG/PT."""
import collections
import json
import pathlib
import re
from decimal import Decimal

ROOT = pathlib.Path(__file__).resolve().parents[2]
PMO = ROOT / 'documents/400_PGPT/470_PMO'


def cost_sum(items):
    return {key: sum((Decimal(str(item['cost'][key])) for item in items),
                     Decimal('0')) for key in ('low', 'base', 'high')}


def check_cost_rollup(originals, shared, children):
    items = originals + shared
    parents = {item['id']: item for item in items}
    assert len(parents) == len(items), 'duplicate cost parent'
    all_ids = [item['id'] for item in items + children]
    assert len(all_ids) == len(set(all_ids)), 'duplicate execution ID'
    grouped = collections.defaultdict(list)
    for child in children:
        assert child['parent'] in parents, 'missing cost parent'
        grouped[child['parent']].append(child)
        assert child['status'] == 'UNASSESSED_NOT_ACCEPTED', 'unverified child credit'
    for item in items + children:
        cost = item['cost']
        assert cost['unit'] == 'weekly_quota_percentage_points'
        assert Decimal('0') <= Decimal(str(cost['low'])) <= Decimal(str(cost['base'])) <= Decimal(str(cost['high'])), 'cost range'
        assert cost['actualSpentPp'] is None, 'unmeasured actual allocation'
        assert cost['costScope'] and cost['estimateBasis'] and cost['confidence']
    for parent_id, group in grouped.items():
        parent = parents[parent_id]
        assert parent['cost']['countsInTotal'] is False, 'parent-child double count'
        assert cost_sum(group) == cost_sum([parent]), 'child cost mismatch'
        assert all(child['cost']['countsInTotal'] for child in group)
    for item in items:
        if item['id'] not in grouped:
            assert item['cost']['countsInTotal'], 'missing leaf budget'
    leaves = [item for item in items if item['id'] not in grouped] + children
    assert cost_sum(leaves) == cost_sum(items), 'rollup total mismatch'
    return leaves, grouped


def check_quota_window(points, intervals, reset):
    assert reset == 1791580290
    assert [point['id'] for point in points] == ['Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5']
    assert all(point['resetEpochSeconds'] == reset for point in points), 'mixed reset'
    assert len(intervals) == len(points) - 1
    for before, after, interval in zip(points, points[1:], intervals):
        assert before['timeJST'] < after['timeJST'], 'time order'
        assert interval['start'] == before['id'] and interval['end'] == after['id']
        assert interval['observedPp'] == after['usedPercent'] - before['usedPercent'], 'quota delta'
        assert interval['observedPp'] >= 0
    return sum(interval['observedPp'] for interval in intervals)


def verify_cost(master):
    budget = json.loads((PMO / '484_WBSコスト枠・細分化.json').read_text())
    originals = [{'id': task['id'], 'cost': task['remainingCost']}
                 for task in master['tasks']]
    shared, children = budget['sharedBudgets'], budget['children']
    leaves, grouped = check_cost_rollup(originals, shared, children)
    assert len(originals) == 190 and len(shared) == 3 and len(children) == 77
    assert len(leaves) == budget['subdivisionRule']['executionLeaves'] == 249
    assert sum(parent in {t['id'] for t in originals} for parent in grouped) == 19
    assert len(grouped) == 21
    # All expensive concrete work must have sub-work; an unidentified reserve is not invented work.
    for item in originals + shared:
        if item['cost']['base'] >= 4 or item['cost']['high'] >= 8:
            assert item['id'] in grouped or item['id'] == 'WBS-K02'
    totals = budget['totals']
    for key, items in [('original190', originals), ('shared', shared), ('remaining', leaves)]:
        assert cost_sum(items) == {name: Decimal(str(value)) for name, value in totals[key].items()}
    assert totals['remaining'] == {'low': 87.2, 'base': 260.85, 'high': 623}
    for kind, summary in totals['byKind'].items():
        group = [{'cost': task['remainingCost']} for task in master['tasks']
                 if task['kind'] == kind]
        assert len(group) == summary['items']
        assert cost_sum(group) == {key: Decimal(str(summary[key])) for key in ('low', 'base', 'high')}
    assert totals['wholeEffortCompletionRate'] is None and not totals['formalAcceptanceChanged']
    assert master['costRevision'] == budget['revision']
    assert master['costBudgetRef'] == '484_WBSコスト枠・細分化.json'
    bases = {basis['id'] for basis in budget['calibration']['bases']}
    assert all(item['cost']['estimateBasis'] in bases for item in originals + shared + children)
    child_ids = {child['id'] for child in children}
    closed = set()

    def visit_child(node, active):
        assert node not in active, 'child dependency cycle'
        if node in closed:
            return
        child = next(item for item in children if item['id'] == node)
        assert child['exitCriteria'] and child['externalDependencies']
        for dependency in child['dependencies']:
            assert dependency in child_ids
            visit_child(dependency, active | {node})
        closed.add(node)

    for child in children:
        visit_child(child['id'], set())
    points, intervals = budget['quotaWindow']['points'], budget['quotaWindow']['intervals']
    assert check_quota_window(points, intervals, budget['quotaWindow']['resetEpochSeconds']) == budget['quotaWindow']['totalObservedPp'] == 80
    for point in points:
        text = (ROOT / point['source']).read_text()
        start = text.index(point['anchor'])
        end = text.find('\n## ', start + len(point['anchor']))
        block = text[start:end if end != -1 else None]
        assert point['needle'] in block, 'quota evidence anchor'
        assert re.search(r'used\s*' + str(point['usedPercent']) + r'(?!\d)', point['needle'])
    table = (PMO / '479_詳細WBS・進捗算定規則.md').read_text()
    for item in originals:
        rows = [line for line in table.splitlines() if line.startswith('| ' + item['id'] + ' |')]
        assert len(rows) == 1
        expected = ' / '.join(f"{item['cost'][key]:.2f}" for key in ('low', 'base', 'high'))
        assert rows[0].endswith(' ' + expected + ' |'), 'human/JSON cost drift'
    detail = (PMO / '483_WBS週次コスト枠・較正方針.md').read_text()
    assert all(detail.count('| ' + child['id'] + ' |') == 1 for child in children)
    for child in children:
        row = next(line for line in detail.splitlines() if line.startswith('| ' + child['id'] + ' |'))
        values = [Decimal(cell.strip()) for cell in row.split('|')[-4:-1]]
        assert values == [Decimal(str(child['cost'][key])) for key in ('low', 'base', 'high')], 'child table cost drift'
    # Cost-only negative canaries: this tool is not a Production test or acceptance gate.
    parent = {'id': 'P', 'cost': {'unit': 'weekly_quota_percentage_points',
              'low': 1, 'base': 2, 'high': 3, 'actualSpentPp': None,
              'costScope': 'canary', 'estimateBasis': 'canary', 'confidence': 'LOW',
              'countsInTotal': True}}
    child = {'id': 'P.01', 'parent': 'P', 'status': 'UNASSESSED_NOT_ACCEPTED', 'cost': dict(parent['cost'])}
    for bad_parent, bad_child in [(parent, child),
        ({**parent, 'cost': {**parent['cost'], 'countsInTotal': False}},
         {**child, 'cost': {**child['cost'], 'base': 2.5}})]:
        try:
            check_cost_rollup([bad_parent], [], [bad_child])
        except AssertionError:
            pass
        else:
            raise AssertionError('cost canary missed')
    try:
        bad_points = [dict(point) for point in points]
        bad_points[1]['resetEpochSeconds'] += 1
        check_quota_window(bad_points, intervals, budget['quotaWindow']['resetEpochSeconds'])
    except AssertionError:
        pass
    else:
        raise AssertionError('reset canary missed')
    return {'unit': budget['unit'], 'remainingCost': totals['remaining'],
            'splitOriginalParents': 19, 'splitSharedParents': 2,
            'children': len(children), 'executionLeaves': len(leaves),
            'observedSharedQuotaPp': 80, 'perWbsActualNotMeasured': True,
            'formalAcceptanceChanged': False}


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
            'costAudit': verify_cost(master),
            'baselineCounterClosed': len(old), 'currentCounterClosed': len(closed),
            'newlyCounterClosed': len(closed - old), 'reopened': len(old - closed),
            'netCounterClosed': len(closed) - len(old), 'statusCounts': counts,
            'scopeAuditStillPending': 'WBS-G13', 'formalAcceptanceChanged': False,
            'businessImplementationChanged': False}


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
