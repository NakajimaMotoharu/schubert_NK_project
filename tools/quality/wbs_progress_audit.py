"""Read-only versioned WBS validation; never grants Production acceptance.

Default: current 481/484/485/486. --baseline-v1: immutable Git 65eddc + 482.
Actual tests/VM/collectors are never executed. Evidence semantics still need review.
"""
import argparse
import collections
import hashlib
import json
import pathlib
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from decimal import Decimal
import wbs_candidate_trace as candidate_trace
import wbs_current_source_structure as current_source_structure

ROOT = pathlib.Path(__file__).resolve().parents[2]
PMO = ROOT / 'documents/400_PGPT/470_PMO'
BASELINE = '65eddc1a290167c0edfdc99673b79f3d8e99a3fd'
UNIT = 'weekly_quota_percentage_points'
COST_KEYS = ('low', 'base', 'high')
STATUS = {'NOT_ACCEPTED', 'IN_PROGRESS', 'BLOCKED', 'RECHECK_REQUIRED', 'ACCEPTED'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate WBS JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coverage_root(value):
    require(isinstance(value, str) and value and '\\' not in value
            and not any(part in {'.', '..'} for part in value.split('/')), 'canonical coverage path required')
    path = pathlib.Path(value)
    return path if path.is_absolute() else ROOT / path


def cost_sum(items):
    return {k: sum((Decimal(str(x['cost'][k])) for x in items), Decimal(0))
            for k in COST_KEYS}


def check_graph(graph):
    closed = set()

    def visit(node, active):
        require(node in graph, 'missing dependency: ' + node)
        require(node not in active, 'dependency cycle: ' + node)
        if node in closed:
            return
        for dependency in graph[node]:
            visit(dependency, active | {node})
        closed.add(node)

    for node in graph:
        visit(node, set())


def check_quota_window(points, intervals, reset):
    require(len({p['id'] for p in points}) == len(points), 'duplicate quota point')
    require(all(p['resetEpochSeconds'] == reset for p in points), 'mixed reset')
    require(len(intervals) == max(0, len(points) - 1), 'quota interval count')
    for before, after, interval in zip(points, points[1:], intervals):
        require(before['timeJST'] < after['timeJST'], 'quota time order')
        require(all(0 <= p['usedPercent'] <= 100 for p in (before, after)), 'quota value')
        require(interval['start'] == before['id'] and interval['end'] == after['id'], 'quota anchor')
        require(interval['observedPp'] == after['usedPercent'] - before['usedPercent'] >= 0, 'quota delta')
    return sum(x['observedPp'] for x in intervals)


def check_actual(cost):
    observations = cost.get('actualObservations', [])
    measured = Decimal(0)
    for item in observations:
        require(item.get('observationId'), 'actual observation ID missing')
        before, after = item['before'], item['after']
        require(before['resetEpochSeconds'] == after['resetEpochSeconds'], 'actual crosses reset')
        require(before['timeJST'] < after['timeJST'], 'actual time order')
        require(all(0 <= p['usedPercent'] <= 100 for p in (before, after)), 'actual quota range')
        delta = after['usedPercent'] - before['usedPercent']
        require(delta >= 0 and item['observedSharedPp'] == delta, 'actual quota delta')
        require(item.get('source') and item.get('run') and item.get('evidence'), 'actual work evidence missing')
        for evidence in item['evidence']:
            require((ROOT / evidence).is_file(), 'actual evidence missing')
        allocation = item.get('allocatedPp')
        if allocation is not None:
            require(item['attribution'] == 'SOLE_WBS' and item.get('otherChatUsageKnown') is True
                    and item.get('otherChatUsedPp') == 0, 'unproven individual attribution')
            require(Decimal(str(allocation)) == Decimal(delta), 'partial arbitrary allocation')
            measured += Decimal(str(allocation))
    actual = cost['actualSpentPp']
    if actual is not None:
        require(observations and Decimal(str(actual)) == measured, 'actual requires measured allocation')
    else:
        require(measured == 0, 'measured allocation omitted')


def check_cost_rollup(originals, shared, children):
    items = originals + shared
    parents = {x['id']: x for x in items}
    require(len(parents) == len(items), 'duplicate cost parent')
    require(len({x['id'] for x in items + children}) == len(items + children), 'duplicate execution ID')
    grouped = collections.defaultdict(list)
    for child in children:
        require(child['parent'] in parents, 'missing cost parent')
        grouped[child['parent']].append(child)
    for item in items + children:
        cost = item['cost']
        require(cost['unit'] == UNIT, 'cost unit')
        require(Decimal(0) <= Decimal(str(cost['low'])) <= Decimal(str(cost['base']))
                <= Decimal(str(cost['high'])), 'cost range')
        require(cost['costScope'] and cost['estimateBasis'] and cost['confidence'], 'cost basis missing')
        check_actual(cost)
    for parent_id, group in grouped.items():
        require(not parents[parent_id]['cost']['countsInTotal'], 'parent-child double count')
        require(cost_sum(group) == cost_sum([parents[parent_id]]), 'child cost mismatch')
        require(all(c['cost']['countsInTotal'] for c in group), 'non-counting child')
    for item in originals:
        if item.get('executionRole') == 'REFERENCE_ONLY':
            require(item.get('sharedWorkRef') in parents, 'missing shared owner')
            require(not item['cost']['countsInTotal'] and all(item['cost'][k] == 0 for k in COST_KEYS), 'alias cost double count')
        elif item['id'] not in grouped:
            require(item['cost']['countsInTotal'], 'missing leaf budget')
    leaves = [x for x in items if x['id'] not in grouped and x['cost']['countsInTotal']] + children
    require(cost_sum(leaves) == cost_sum(items), 'rollup total mismatch')
    allocated_ids = [o['observationId'] for leaf in leaves for o in leaf['cost'].get('actualObservations', [])
                     if o.get('allocatedPp') is not None]
    require(len(allocated_ids) == len(set(allocated_ids)), 'actual observation allocated twice')
    return leaves, grouped


def selected_measurement(row, production_source, prior_root):
    """Pinned per-WBS selected result, never a mixed-source formal whole-run claim."""
    override = row['measurementOverride']
    path = ROOT / override['manifest']
    require(digest(path) == override['manifestSha256'], 'selected manifest hash')
    manifest = read_json(path)
    require(manifest['source'] == override['source']
            and re.fullmatch('[0-9a-f]{40}', manifest['source'])
            and manifest['productionSource'] == production_source
            and manifest['run'] == override['run']
            and row['id'] in manifest['wbsIds'], 'selected source/run/WBS mismatch')
    require(manifest['actualExit'] == manifest['FES'] == manifest['staticIssues'] == 0
            and manifest['sourceUnchanged'] is True
            and manifest['formalUpdated'] is False
            and manifest['acceptedWbsDelta'] == 0, 'selected incomplete/formal claim')
    stem = pathlib.Path(manifest['runRecordStem'])
    require(pathlib.Path(str(stem) + '.source').read_text().strip() == manifest['source']
            and pathlib.Path(str(stem) + '.exit').read_text().strip() == '0'
            and digest(pathlib.Path(str(stem) + '.log')) == manifest['logSha256'], 'selected run record')
    data = {}
    for module in manifest['modules']:
        name = module['module']
        require(name not in data, 'selected duplicate module')
        directory = pathlib.Path(manifest['coverageRoot']) / name
        xml = directory / 'site/jacoco/jacoco.xml'
        jar = directory / ('schubert-nk-' + name + '-0.1.0-SNAPSHOT.jar')
        prior = pathlib.Path(module['priorJar'])
        require(prior == pathlib.Path(prior_root) / name / jar.name, 'selected baseline jar binding')
        require(digest(xml) == module['coverageXmlSha256']
                and digest(jar) == module['jarSha256']
                and digest(prior) == module['priorJarSha256'], 'selected artifact hash')
        with zipfile.ZipFile(jar) as fresh, zipfile.ZipFile(prior) as original:
            a = [n for n in fresh.namelist() if n.endswith('.class')]
            b = [n for n in original.namelist() if n.endswith('.class')]
            require(len(a) == len(set(a)) and len(b) == len(set(b)) and set(a) == set(b),
                    'selected production class inventory')
            require(all(fresh.read(n) == original.read(n) for n in a), 'selected production byte drift')
        static = directory / 'spotbugsXml.xml'
        require(digest(static) == module['spotbugsXmlSha256']
                and not ET.parse(static).getroot().findall('.//BugInstance'), 'selected static result')
        suites = [ET.parse(p).getroot() for p in (directory / 'surefire-reports').glob('TEST-*.xml')]
        pt = {k: sum(int(s.attrib.get(k, 0)) for s in suites)
              for k in ('tests', 'failures', 'errors', 'skipped')}
        require(pt == module['pt'] and pt['tests'] > 0
                and pt['failures'] == pt['errors'] == pt['skipped'] == 0, 'selected XML result')
        groups = {}
        for node in ET.parse(xml).getroot().findall('./package/class'):
            family = node.attrib['name'].split('$')[0]
            values = groups.setdefault(family, {k: [0, 0] for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')})
            for counter in node.findall('counter'):
                if counter.attrib['type'] in values:
                    pair = values[counter.attrib['type']]
                    pair[0] += int(counter.attrib['missed'])
                    pair[1] += int(counter.attrib['covered'])
        data[name] = groups
    require(data, 'selected empty modules')
    return data


def check_measurement(snapshot, inventory):
    binding = inventory['measurementBindings']
    manifest = read_json(ROOT / binding['manifest'])
    require(binding['source'] == snapshot['source'] == manifest['productionSource'], 'measurement source mismatch')
    require(binding['run'] == snapshot['measurementRun'], 'measurement run mismatch')
    require(manifest['actualExit'] == manifest['FES'] == manifest['staticIssues'] == 0,
            'failed/partial host run')
    types = ('LINE', 'METHOD', 'CLASS', 'BRANCH')
    data = {}
    for module in manifest['modules']:
        path = coverage_root(binding['coverageRoot']) / module['module'] / 'site/jacoco/jacoco.xml'
        require(path.is_file() and digest(path) == module['coverageXmlSha256'], 'measurement XML hash')
        grouped = {}
        for node in ET.parse(path).getroot().findall('./package/class'):
            name = node.attrib['name'].split('$')[0]
            value = grouped.setdefault(name, {k: [0, 0] for k in types})
            for counter in node.findall('counter'):
                if counter.attrib['type'] in value:
                    pair = value[counter.attrib['type']]
                    pair[0] += int(counter.attrib['missed'])
                    pair[1] += int(counter.attrib['covered'])
        data[module['module']] = grouped
    for row in snapshot['rows']:
        if 'measuredFamilies' not in row:
            continue
        row_data = selected_measurement(row, snapshot['source'], binding['coverageRoot']) if 'measurementOverride' in row else data
        if 'measurementOverride' in row:
            require(all(a['module'] in row_data for a in inventory['artifacts']
                        if a['owner'] == row['id'] and a['kind'] == 'JAVA' and a['module'] in data),
                    'selected omitted owner module')
        targets = [a for a in inventory['artifacts'] if a['owner'] == row['id']
                   and a['kind'] == 'JAVA' and a['module'] in row_data]
        counters = []
        declaration_only = 0
        for artifact in targets:
            counter = row_data[artifact['module']].get(artifact['class'])
            if artifact.get('counterApplicability') == 'NO_EXECUTABLE_INTERFACE':
                require(counter is not None and all(sum(v) == 0 for v in counter.values()),
                        'interface gained executable counters')
                short = artifact['class'].rsplit('/', 1)[-1]
                require(re.search(r'\binterface\s+' + re.escape(short) + r'\b',
                                  (candidate_trace.git_artifacts(snapshot['source'],[artifact['path']])[artifact['path']].decode()
                                   if 'currentPhysicalCandidate' in inventory else (ROOT / artifact['path']).read_text())), 'non-interface counter omission')
                declaration_only += 1
            else:
                counters.append(counter)
        expected = classify([None if c is None else [c[k][z] for k in types for z in (0, 1)]
                             for c in counters]) if counters else (
                                 'NON_EXECUTABLE_CONTRACT_REVIEW' if targets else 'NON_JAVA_EVIDENCE_REQUIRED')
        missed = {k: sum(c[k][0] for c in counters if c is not None) for k in types}
        require(row['measuredFamilies'] == len(counters) and row['missed'] == missed
                and row.get('nonExecutableFamilies', 0) == declaration_only
                and row['measurementStatus'] == expected, 'measurement drift: ' + row['id'])


def check_acceptance(item, source, states):
    acceptance = item['acceptance']
    require(acceptance['status'] in STATUS, 'unknown acceptance state')
    if acceptance['status'] != 'ACCEPTED':
        return
    require(acceptance['source'] == source and acceptance.get('acceptedBy'), 'acceptance source/reviewer missing')
    required = {c['id'] for c in item['acceptanceChecks']}
    require(required == set(acceptance['criteriaSatisfied']), 'acceptance criteria incomplete')
    require(acceptance['evidence'], 'acceptance evidence missing')
    proved = set()
    for evidence in acceptance['evidence']:
        path = ROOT / evidence['path']
        require(path.is_file() and digest(path) == evidence['sha256'], 'acceptance evidence hash')
        require(evidence['source'] == source and evidence.get('run'), 'evidence source/run')
        proved.update(evidence['verifiedChecks'])
    require(required <= proved, 'criteria not backed by evidence')
    for dep in item.get('dependencies', []) + item.get('externalDependencies', []):
        require(states[dep]['status'] == 'ACCEPTED' and states[dep]['source'] == source, 'acceptance dependency open')
    for dep in item.get('children', []):
        require(states[dep]['status'] == 'ACCEPTED' and states[dep]['source'] == source, 'child acceptance open')
    for dep in item.get('externalPrerequisites', []):
        require(dep in acceptance.get('resolvedPrerequisites', []), 'external approval open')


def classify(counters):
    if not counters:
        return 'NO_HOST_MEASUREMENT'
    if any(c is None for c in counters):
        return 'TARGET_ABSENT'
    return ('HOST_COUNTERS_CLOSED' if all(c[5] > 0 and all(c[i] == 0 for i in (0, 2, 4, 6))
                                        for c in counters) else 'HOST_GAPS')


def verify_baseline():
    # Load the historical checker itself, not a mutable copy with current fixed values.
    code = subprocess.check_output(['git', 'show', BASELINE + ':tools/quality/wbs_progress_audit.py'], cwd=ROOT, text=True)
    namespace = {'__file__': str(ROOT / 'tools/quality/wbs_progress_audit.py'), '__name__': 'wbs_historical'}
    exec(compile(code, '<historical wbs audit>', 'exec'), namespace)
    historical_master = json.loads(subprocess.check_output(['git', 'show', BASELINE + ':documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json'], cwd=ROOT, text=True))
    historical_budget = json.loads(subprocess.check_output(['git', 'show', BASELINE + ':documents/400_PGPT/470_PMO/484_WBSコスト枠・細分化.json'], cwd=ROOT, text=True))
    read_json(PMO / '482_WBS実績snapshot_20261007.json')  # Validate frozen JSON; hash is checked below.
    require(digest(PMO / '482_WBS実績snapshot_20261007.json') == read_json(PMO / '481_PGPT詳細WBS.json')['baselineV1']['snapshotSha256'], 'historical snapshot changed')
    # The v1 assertions remain frozen. Supply Git-backed data/docs, never write temporary repo files.
    original_read = pathlib.Path.read_text
    paths = {'481_PGPT詳細WBS.json': json.dumps(historical_master), '484_WBSコスト枠・細分化.json': json.dumps(historical_budget)}
    for name in ['479_詳細WBS・進捗算定規則.md', '483_WBS週次コスト枠・較正方針.md']:
        paths[name] = subprocess.check_output(['git', 'show', BASELINE + ':documents/400_PGPT/470_PMO/' + name], cwd=ROOT, text=True)
    def historical_read(path, *args, **kwargs):
        if path.parent == PMO and path.name in paths:
            return paths[path.name]
        return original_read(path, *args, **kwargs)
    try:
        pathlib.Path.read_text = historical_read
        result = namespace['verify']()
    finally:
        pathlib.Path.read_text = original_read
    result['revisionMode'] = 'IMMUTABLE_V1_GIT_AND_482'
    return result


def verify(master_path=None, snapshot_path=None, budget_path=None, inventory_path=None):
    master = read_json(master_path or PMO / '481_PGPT詳細WBS.json')
    budget = read_json(budget_path or PMO / master['costBudgetRef'])
    snapshot = read_json(snapshot_path or PMO / master['currentSnapshotRef'])
    ip = inventory_path or PMO / master['inventoryRef']
    inventory = read_json(ip)
    tasks, children, shared = master['tasks'], budget['children'], budget['sharedBudgets']
    by = {t['id']: t for t in tasks}
    require(len(by) == len(tasks) == snapshot['allTasks'], 'duplicate/missing WBS ID')
    require(master['revision'] == snapshot['revision'] == inventory['revision'] == budget['measurementWbsRevision'], 'revision mismatch')
    require(master['costRevision'] == budget['revision'], 'cost revision mismatch')
    require(snapshot['source'] == inventory['source'], 'inventory source mismatch')
    require(snapshot['inventorySha256'] == digest(ip), 'inventory hash mismatch')
    require({t['program'] for t in tasks} == {p['program'] for p in master['programs']}, 'Program mismatch')
    states = {t['id']: t['acceptance'] for t in tasks + children}
    graph = {t['id']: t['dependencies'] + t.get('children', []) for t in tasks}
    graph.update({c['id']: c['dependencies'] + c['externalDependencies'] for c in children})
    check_graph(graph)
    # Budget-only K leaves are not Production acceptance states; they still obey a DAG.
    for t in tasks + children:
        require(t['exitCriteria'] and t['acceptanceChecks'], 'missing individual exit checks')
        require(len({c['id'] for c in t['acceptanceChecks']}) == len(t['acceptanceChecks']), 'duplicate criterion')
        check_acceptance(t, snapshot['source'], states)
    originals = [{'id': t['id'], 'cost': t['remainingCost'], 'executionRole': t['executionRole'],
                  'sharedWorkRef': t.get('sharedWorkRef')} for t in tasks]
    leaves, grouped = check_cost_rollup(originals, shared, children)
    require(len(leaves) == snapshot['executionLeaves'] == budget['subdivisionRule']['executionLeaves'], 'leaf count')
    for key, items in [('original190', originals), ('shared', shared), ('remaining', leaves)]:
        require(cost_sum(items) == {k: Decimal(str(v)) for k, v in budget['totals'][key].items()}, 'cost total: ' + key)
    for kind, totals in budget['totals']['byKind'].items():
        group = [t for t in originals if by[t['id']]['kind'] == kind]
        require(len(group) == totals['items'] and cost_sum(group) == {k: Decimal(str(totals[k])) for k in COST_KEYS}, 'kind total')
    window = budget['quotaWindow']
    require(check_quota_window(window['points'], window['intervals'], window['resetEpochSeconds']) == window['totalObservedPp'], 'observed quota total')
    artifacts = inventory['artifacts']
    require(len({x['path'] for x in artifacts}) == len(artifacts), 'duplicate artifact ownership')
    historical = candidate_trace.git_artifacts(inventory['source'],[x['path']for x in artifacts]) if 'currentPhysicalCandidate' in inventory else None
    for x in artifacts:
        require(x['owner'] in by and by[x['owner']]['executionRole'] != 'REFERENCE_ONLY', 'artifact alias/unknown owner')
        require((hashlib.sha256(historical[x['path']]).hexdigest()==x['sha256']) if historical is not None
                else ((ROOT / x['path']).is_file() and digest(ROOT / x['path']) == x['sha256']), 'artifact missing/changed: ' + x['path'])
        require(x['costOwner'] == x['owner'], 'common manufacture cost owner mismatch')
    tracked = candidate_trace.git_files(inventory['source']) if historical is not None else subprocess.check_output(['git', 'ls-files', 'src', 'program/characterization'], cwd=ROOT, text=True).splitlines()
    expected = {p for p in tracked if ('/src/main/java/' in p and p.endswith('.java'))
                or '/src/main/resources/' in p or p.startswith('src/deployment/')}
    require(expected == {x['path'] for x in artifacts}, 'physical inventory scope missing/extra')
    current_candidate = candidate_trace.verify_candidate(inventory) if historical is not None else None
    if current_candidate is not None:
        require(snapshot.get('currentPhysicalCandidateMeasurement')==current_candidate,'current candidate technical snapshot drift')
    required = []
    for f in (ROOT / 'documents/100_RD').rglob('*.md'):
        for line in f.read_text().splitlines():
            match = re.match(r'^\|\s*`?([A-Z]+(?:-[A-Z]+)?-\d{3}|MSG-F\d{2}|T-\d{3})`?\s*\|', line)
            if match:
                required.append(match[1])
    require(len(required) == len(set(required)) and set(required) == {x['id'] for x in inventory['requirements']}, 'RD inventory missing/duplicate')
    for x in inventory['requirements'] + inventory['layouts']:
        require(x['owner'] in by and (ROOT / x['source']).is_file(), 'trace origin/owner missing')
        origin = (ROOT / x['source']).read_text().splitlines()[x['line'] - 1]
        require(x['id'] in origin, 'trace origin ID changed')
    for x in inventory['requirements']:
        origin = (ROOT / x['source']).read_text().splitlines()[x['line'] - 1]
        require(' / '.join(c.strip() for c in origin.split('|')[2:-1]) == x['requirement'],
                'requirement text changed without trace revision')
    catalog = next((ROOT / 'documents/200_UI/230_インターフェース').glob('233*'))
    layouts = set(re.findall(r'`([A-Z0-9]{8})`', catalog.read_text()))
    require(len(inventory['layouts']) == len(layouts) and layouts == {x['id'] for x in inventory['layouts']},
            'layout inventory missing/duplicate')
    counts = inventory['counts']
    require(counts['rdRequirements'] == len(required) and counts['artifacts'] == len(artifacts)
            and counts['layouts'] == len(layouts) and counts['unassigned'] == 0, 'inventory summary drift')
    require(counts['javaOuterClasses'] == sum(a['kind'] == 'JAVA' and a['module'] != 'characterization' for a in artifacts)
            and counts['packageInfo'] == sum(a['kind'] == 'JAVA_PACKAGE' for a in artifacts)
            and counts['screens'] == len({a['screenId'] for a in artifacts if 'screenId' in a}), 'inventory kind counts')
    for x in inventory['sharedOwnership']:
        require(x['owner'] in by and x['owner'] not in x['consumers'], 'shared ownership loop')
        require(all(c in by for c in x['consumers']), 'shared consumer missing')
    for t in tasks:
        require(set(t['ownedArtifacts']) == {x['path'] for x in artifacts if x['owner'] == t['id']}, 'task artifact join')
        require(set(t['requirementIds']) == {x['id'] for x in inventory['requirements'] if x['owner'] == t['id']}, 'task requirement join')
    current = {r['id']: r for r in snapshot['rows']}
    require(len(current) == len(snapshot['rows']) and set(current) == set(by), 'snapshot task set')
    require(dict(collections.Counter(r['measurementStatus'] for r in current.values())) == snapshot['counts'], 'status count')
    check_measurement(snapshot, inventory)
    for id, row in current.items():
        require(row['acceptance'] == by[id]['acceptance'], 'acceptance snapshot drift')
        for path in row['evidence']:
            require((ROOT / path).exists(), 'snapshot evidence missing')
    historical = PMO / master['historicalSnapshotRef']
    require(digest(historical) == snapshot['historicalSnapshotSha256'] == master['baselineV1']['snapshotSha256'], 'history changed')
    require(snapshot['wholeEffortCompletionRate'] is None, 'unweighted effort rate')
    table = (PMO / '479_詳細WBS・進捗算定規則.md').read_text()
    for t in tasks:
        rows = [r for r in table.splitlines() if r.startswith('| ' + t['id'] + ' |')]
        value = ' / '.join(f"{t['remainingCost'][k]:.2f}" for k in COST_KEYS)
        require(len(rows) == 1 and rows[0].endswith(' ' + value + ' |'), 'human cost table drift')
    return {'revision': master['revision'], 'wbsItems': len(tasks), 'executionLeaves': len(leaves),
            'currentPhysicalCandidate':current_candidate,'canonicalAcceptanceSource':snapshot['source'],
            'inventory': inventory['counts'], 'currentMeasurementCounts': snapshot['counts'],
            'remainingCost': budget['totals']['remaining'], 'acceptedTasks': sum(t['acceptance']['status'] == 'ACCEPTED' for t in tasks),
            'historicalV1Preserved': True, 'formalAcceptanceChangedByAudit': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-v1', action='store_true')
    parser.add_argument('--current-source-structure-only', action='store_true',
                        help='Validate the pinned current static artifact view only; never accepts runtime or the full WBS')
    for key in ['master', 'snapshot', 'budget', 'inventory']:
        parser.add_argument('--' + key, type=pathlib.Path)
    args = parser.parse_args()
    if args.baseline_v1 and args.current_source_structure_only:
        parser.error('historical baseline and current static structure are separate domains')
    if not args.baseline_v1:
        current_master = read_json(args.master or PMO / '481_PGPT詳細WBS.json')
        current_snapshot = read_json(args.snapshot or PMO / current_master['currentSnapshotRef'])
        current_inventory_path = args.inventory or PMO / current_master['inventoryRef']
        current_inventory = read_json(current_inventory_path)
        if args.current_source_structure_only or current_source_structure.VIEW_KEY in current_inventory:
            structure = current_source_structure.verify(ROOT, current_master, current_snapshot,
                                                        current_inventory, inventory_path=current_inventory_path)
            result = (structure if args.current_source_structure_only
                      else current_source_structure.full_audit_hold(structure, current_inventory))
            print(json.dumps(result, ensure_ascii=False, indent=2))
            raise SystemExit(0 if args.current_source_structure_only else 1)
    result = verify_baseline() if args.baseline_v1 else verify(args.master, args.snapshot, args.budget, args.inventory)
    print(json.dumps(result, ensure_ascii=False, indent=2))
