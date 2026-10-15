"""Evidence-bound mechanical current-source WBS rebase; never grants acceptance."""
import collections
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo
import pg3280_wbs_current_source as staged
import wbs_progress_audit as audit

ROOT, PMO, SOURCE, OUT = staged.ROOT, staged.PMO, staged.SOURCE, staged.OUT
INVENTORY = '485_WBS網羅性・受入対応.json'
SNAPSHOT = '486_WBS現行実績.json'


def metadata_descriptions(source, run, tests, suites, classes):
    return {
        'artifactHashMeaning': f'sha256 identifies current physical artifact bytes. source={source} is the current qualified production measurement source; assessmentHead is the management Git HEAD at binding assembly. measurementBindings selects {run}. Frozen prior sources, descriptions and candidate provenance remain historical in measurementBindingHistory/baselineSha256/candidateProvenance. Inventory hash is not code, runtime authority, formal or WBS acceptance.',
        'measurementMode': f'Current same-byte all-six host/native measurement {run}, production source {source}, actual {tests}PT/{suites}suite/{classes}Main. Prior measurement bindings/classifications are historical, not current source claims. Technical counters and individually bound runtime stages do not grant live authority, global100, formal or individual WBS acceptance.'}


def render_value(key, value):
    if key == 'rows':
        return '[\n' + ',\n'.join('    ' + json.dumps(row, ensure_ascii=False) for row in value) + '\n  ]'
    return json.dumps(value, ensure_ascii=False, indent=2).replace('\n', '\n  ')


def rewrite_root(text, updates):
    """Bulk root/row updates retain every other observation and original text span."""
    original = json.loads(text, object_pairs_hook=audit.unique_object)
    decoder = json.JSONDecoder(object_pairs_hook=audit.unique_object)
    start = text.index('{'); index = start + 1; spans = []
    while True:
        while text[index].isspace() or text[index] == ',':
            index += 1
        if text[index] == '}':
            break
        key, index = decoder.raw_decode(text, index)
        while text[index].isspace():
            index += 1
        staged.require(text[index] == ':', 'root key separator required'); index += 1
        while text[index].isspace():
            index += 1
        value_start = index
        _, index = decoder.raw_decode(text, index)
        if key in updates:
            spans.append((value_start, index, render_value(key, updates[key])))
    result = text
    for a, b, replacement in reversed(spans):
        result = result[:a] + replacement + result[b:]
    extras = {k: v for k, v in updates.items() if k not in original}
    if extras:
        addition = ''.join('  ' + json.dumps(k) + ': ' + render_value(k, v) + ',\n' for k, v in extras.items())
        result = result[:start + 1] + '\n' + addition + result[start + 1:].lstrip('\n')
    staged.require(json.loads(result, object_pairs_hook=audit.unique_object) == {**original, **updates}, 'only planned root updates allowed')
    return result


def group_coverage(manifest):
    result = {}
    for module in manifest['modules']:
        name = module['module']; staged.require(name not in result, 'duplicate measurement module forbidden')
        path = audit.coverage_root(manifest['coverageRoot']) / name / 'site/jacoco/jacoco.xml'
        staged.require(path.is_file() and staged.sha(path.read_bytes()) == module['coverageXmlSha256'], 'public measurement hash required')
        families = {}
        for node in ET.parse(path).getroot().findall('./package/class'):
            family = node.get('name').split('$')[0]
            counts = families.setdefault(family, {k: [0, 0] for k in staged.COUNTERS})
            for counter in node.findall('counter'):
                if counter.get('type') in counts:
                    counts[counter.get('type')][0] += int(counter.get('missed'))
                    counts[counter.get('type')][1] += int(counter.get('covered'))
        result[name] = families
    staged.require(set(result) == set(staged.MODULES), 'all six modules required')
    return result


def reclassified_rows(inventory, snapshot, manifest, data):
    rows = copy.deepcopy(snapshot['rows'])
    mapped = set(manifest['runtimeVerifiedRows'])
    staged.require(mapped == {'WBS-N05', 'WBS-N06', 'WBS-N07', 'WBS-N08', 'WBS-N09', 'WBS-N10', 'WBS-N12', 'WBS-N14'}, 'only explicitly re-proved runtime rows allowed')
    evidence = str(staged.PUBLIC / 'manifest.json')
    for row in rows:
        prior = {k: copy.deepcopy(row[k]) for k in ['measurementStatus', 'measuredFamilies', 'missed',
                                                  'nonExecutableFamilies', 'measurementOverride', 'evidence'] if k in row}
        prior.update(sourceBinding=snapshot['source'], measurementRun=snapshot['measurementRun'])
        row.setdefault('historicalMeasurements', []).append(prior)
        if 'measuredFamilies' in row:
            targets = [a for a in inventory['artifacts'] if a['owner'] == row['id'] and a['kind'] == 'JAVA' and a['module'] in data]
            counts = []; declarations = 0
            for artifact in targets:
                counter = data[artifact['module']].get(artifact['class'])
                if artifact.get('counterApplicability') == 'NO_EXECUTABLE_INTERFACE':
                    staged.require(counter is not None and all(sum(v) == 0 for v in counter.values()), 'declaration must still have zero executable counters')
                    declarations += 1
                else:
                    counts.append(counter)
            status = audit.classify([None if c is None else [c[k][z] for k in staged.COUNTERS for z in (0, 1)] for c in counts]) if counts else ('NON_EXECUTABLE_CONTRACT_REVIEW' if targets else 'NON_JAVA_EVIDENCE_REQUIRED')
            row.update(measurementStatus=status, measuredFamilies=len(counts),
                       missed={k: sum(c[k][0] for c in counts if c is not None) for k in staged.COUNTERS},
                       nonExecutableFamilies=declarations, measurementSource=SOURCE)
            row.pop('measurementOverride', None)
            row['evidence'] = [*row['evidence'], evidence]
        elif row['id'] in mapped:
            row.update(measurementStatus='VM_STEP_VERIFIED', measurementSource=SOURCE,
                       currentLiveAuthority=False, evidence=[*row['evidence'], evidence])
        elif row['measurementStatus'] == 'VM_STEP_VERIFIED':
            row.update(measurementStatus='HISTORICAL_VM_SUCCESS_RECHECK', measurementSource=snapshot['source'],
                       sourceRecheckReason='Historical proof not individually mapped to a9; no new execution or acceptance inferred')
        staged.require(row['acceptance'] == next(r['acceptance'] for r in snapshot['rows'] if r['id'] == row['id']), 'acceptance must not change during measurement rebase')
    return rows


def replace_public(path, data):
    # All prior bytes are preserved privately and both candidate files pass the
    # strict audit before either is replaced. Targets are two explicit files.
    with tempfile.NamedTemporaryFile(prefix='.pg3282-', suffix='.json', dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name); stream.write(data); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def main():
    os.umask(0o077)
    staged.require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'committed staged proof/clean worktree required')
    staged.require(not (OUT / 'apply-intent.safe.json').exists(), 'one new application only; interrupted application requires exact intent recovery')
    receipt = staged.read(OUT / 'manifest.safe.json'); public_path = ROOT / receipt['publicManifest']
    staged.require(receipt['actualExit'] == 0 and receipt['applied'] is False
                   and staged.sha(public_path.read_bytes()) == receipt['publicManifestSha256'], 'exact committed staged authority required')
    manifest = staged.read(public_path)
    staged.require(manifest['productionSource'] == SOURCE and manifest['acceptedLeafDelta'] == 0, 'current source/nonacceptance projection required')
    staged.authorities(staged.read(staged.W / 'pg3276-header-group-full-qualified-v1/manifest.safe.json'), staged.read(staged.W / 'pg3278-header-group-native-qualified-v1/manifest.safe.json'))
    before_audit = audit.verify()
    texts = {n: (PMO / n).read_text() for n in [INVENTORY, SNAPSHOT]}
    staged.require(all(staged.sha(texts[n].encode()) == manifest['beforeFileHashes'][n] for n in texts), 'no concurrent inventory/snapshot changes allowed')
    inventory = json.loads(texts[INVENTORY], object_pairs_hook=audit.unique_object)
    snapshot = json.loads(texts[SNAPSHOT], object_pairs_hook=audit.unique_object)
    staged.require(inventory['source'] == snapshot['source'] == manifest['beforeSource']
                   and inventory['measurementBindings'] == manifest['beforeBinding'], 'exact old binding required')
    paths = [a['path'] for a in inventory['artifacts']]
    staged.require(len(paths) == 941 and not subprocess.check_output(['git', 'diff', SOURCE, 'HEAD', '--', *paths], cwd=ROOT), 'all current941 artifacts must still equal production source')
    data = group_coverage(manifest); rows = reclassified_rows(inventory, snapshot, manifest, data)
    staged.require(len(rows) == 190 and len({r['id'] for r in rows}) == 190, 'same190 unique rows required')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    history = {'source': inventory['source'], 'binding': inventory['measurementBindings'],
               'artifactHashMeaningAtPreviousBinding': inventory.get('artifactHashMeaning'),
               'snapshotMeasurementModeAtPreviousBinding': snapshot.get('measurementMode'),
               'snapshotAsOfAtPreviousBinding': snapshot.get('asOf'),
               'inventorySha256': manifest['beforeFileHashes'][INVENTORY], 'snapshotSha256': manifest['beforeFileHashes'][SNAPSHOT],
               'preservedGitHead': head, 'newMeasurementManifestSha256': receipt['publicManifestSha256']}
    binding = {'source': SOURCE, 'run': manifest['run'], 'coverageRoot': manifest['coverageRoot'], 'manifest': str(staged.PUBLIC / 'manifest.json')}
    descriptions = metadata_descriptions(SOURCE, manifest['run'], manifest['tests'], manifest['suites'], manifest['mainClasses'])
    inventory_text = rewrite_root(texts[INVENTORY], {'source': SOURCE, 'assessmentHead': head,
                         'artifactHashMeaning': descriptions['artifactHashMeaning'],
                         'measurementBindings': binding, 'measurementBindingHistory': [*inventory.get('measurementBindingHistory', []), history]})
    record = {'source': SOURCE, 'run': manifest['run'], 'oldSource': snapshot['source'],
              'scopeChanged': False, 'acceptedLeafDelta': 0, 'effortPercent': None,
              'technicalReclassificationIsNotNewManufacture': True, 'runtimeHistoricalClaimsRequalifiedIndividually': True}
    snapshot_text = rewrite_root(texts[SNAPSHOT], {'source': SOURCE, 'measurementRun': manifest['run'],
                         'measurementMode': descriptions['measurementMode'],
                         'asOf': datetime.datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(),
                         'inventorySha256': staged.sha(inventory_text.encode()), 'rows': rows,
                         'counts': dict(collections.Counter(r['measurementStatus'] for r in rows)),
                         'currentSourceMeasurementRebase20261015': record})
    pending_inventory = OUT / 'candidate-inventory.private.json'; pending_snapshot = OUT / 'candidate-snapshot.private.json'
    with pending_inventory.open('x') as stream:
        stream.write(inventory_text)
    with pending_snapshot.open('x') as stream:
        stream.write(snapshot_text)
    candidate = audit.verify(inventory_path=pending_inventory, snapshot_path=pending_snapshot)
    staged.require(candidate['acceptedTasks'] == before_audit['acceptedTasks'], 'measurement rebase cannot grant acceptance')
    intent = {'oldHashes': manifest['beforeFileHashes'], 'newHashes': {INVENTORY: staged.sha(inventory_text.encode()), SNAPSHOT: staged.sha(snapshot_text.encode())}, 'source': SOURCE, 'publicManifestSha256': receipt['publicManifestSha256'], 'createdUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with (OUT / 'apply-intent.safe.json').open('x') as stream:
        json.dump(intent, stream, sort_keys=True); stream.flush(); os.fsync(stream.fileno())
    for name, text in [(INVENTORY, inventory_text), (SNAPSHOT, snapshot_text)]:
        staged.require(staged.sha((PMO / name).read_bytes()) == intent['oldHashes'][name], 'exact pre-replacement bytes required')
        replace_public(PMO / name, text.encode())
    final = audit.verify()
    result = {'actualExit': 0, 'source': SOURCE, 'run': manifest['run'], 'beforeCounts': before_audit['currentMeasurementCounts'],
              'afterCounts': final['currentMeasurementCounts'], 'acceptedTasksBefore': before_audit['acceptedTasks'],
              'acceptedTasksAfter': final['acceptedTasks'], 'acceptedLeafDelta': 0, 'scopeChanged': False,
              'formalAccepted': False, 'effortPercent': None, 'applied': True, 'hashes': intent['newHashes']}
    with (OUT / 'applied.safe.json').open('x') as stream:
        json.dump(result, stream, sort_keys=True)
    print(json.dumps(result)); return 0


if __name__ == '__main__':
    raise SystemExit(main())
