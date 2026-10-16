"""Journalled measurement-only update: same source941 artifacts/17 acceptances, no new credit."""
import argparse
import collections
import copy
import datetime
import hashlib
import json
import os
import subprocess
from zoneinfo import ZoneInfo
import wbs_progress_audit as audit
from pg3282_wbs_current_source_apply import group_coverage, rewrite_root, replace_public, metadata_descriptions
from pg3928_current_boundary_full_six import ROOT, W, SOURCE, require

PMO = ROOT / 'documents/400_PGPT/470_PMO'
NAMES = ('481_PGPT詳細WBS.json', '484_WBSコスト枠・細分化.json', '485_WBS網羅性・受入対応.json', '486_WBS現行実績.json')
OUT = W / 'pg3956-wbs-same-source-measurement-v1'
PROOF = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3954-current-boundary-qualified-v1/manifest.json'
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def candidates(texts, proof):
    require(proof['actualExit'] == 0 and proof['productionSource'] == SOURCE and (proof['tests'], proof['suites'], proof['mainClasses'], proof['FES']) == (3716, 545, 1643, 0), 'exact actual current whole')
    require(proof['allOriginal3714CasesRetained'] is True and proof['all1643PhysicalMainUnchanged'] is True and proof['nativeStreams'] == 18 and proof['nativePoints'] == 20 and proof['historicalSourceNativeImported'] is False and proof['acceptedLeafDelta'] == 0 and proof['formalAccepted'] is False, 'unchanged physical/independent Test scope and no acceptance')
    require(proof['remaining'] == {k: sum(v[k]['missed'] for v in proof['moduleCounters'].values()) for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')} and proof['F03Accepted'] is False and proof['staticIssues'] == 0, 'same six exact counters, no F03 promotion')
    inventory, snapshot = (json.loads(texts[n], object_pairs_hook=audit.unique_object) for n in NAMES[2:])
    require(inventory['source'] == snapshot['source'] == SOURCE and len(inventory['artifacts']) == 941, 'same actual source, not source rebase')
    require(all(sha((ROOT / a['path']).read_bytes()) == a['sha256'] for a in inventory['artifacts']), 'all941 current physical artifact hashes still exact')
    data = group_coverage(proof); rows = copy.deepcopy(snapshot['rows'])
    for row in rows:
        if 'measuredFamilies' not in row: continue
        row.setdefault('historicalMeasurements', []).append({k: row[k] for k in ['measurementStatus', 'measurementSource', 'measuredFamilies', 'missed', 'nonExecutableFamilies'] if k in row} | {'measurementRun': snapshot['measurementRun']})
        owned = [a for a in inventory['artifacts'] if a['owner'] == row['id'] and a['kind'] == 'JAVA' and a['module'] in data]
        counts = []; declarations = 0
        for artifact in owned:
            count = data[artifact['module']].get(artifact['class'])
            if artifact.get('counterApplicability') == 'NO_EXECUTABLE_INTERFACE':
                require(count is not None and all(sum(v) == 0 for v in count.values()), 'unchanged declaration-only contract')
                declarations += 1
            else: counts.append(count)
        status = audit.classify([None if c is None else [c[k][z] for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH') for z in (0, 1)] for c in counts]) if counts else ('NON_EXECUTABLE_CONTRACT_REVIEW' if owned else 'NON_JAVA_EVIDENCE_REQUIRED')
        row.update(measurementStatus=status, measurementSource=SOURCE, measuredFamilies=len(counts), nonExecutableFamilies=declarations,
                   missed={k: sum(c[k][0] for c in counts if c is not None) for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')})
        row['evidence'] = [*row['evidence'], str(PROOF.relative_to(ROOT))]
    binding = {'source': SOURCE, 'run': proof['run'], 'coverageRoot': proof['coverageRoot'], 'manifest': str(PROOF.relative_to(ROOT))}
    descriptions = metadata_descriptions(SOURCE, proof['run'], 3716, 545, 1643)
    inv = rewrite_root(texts[NAMES[2]], {'measurementBindings': binding, 'artifactHashMeaning': descriptions['artifactHashMeaning'],
        'measurementBindingHistory': [*inventory.get('measurementBindingHistory', []), {'source': SOURCE, 'binding': inventory['measurementBindings'], 'inventorySha256': sha(texts[NAMES[2]].encode()), 'snapshotSha256': sha(texts[NAMES[3]].encode()), 'newAcceptedLeafDelta': 0, 'physicalArtifactChanges': 0}]})
    snap = rewrite_root(texts[NAMES[3]], {'measurementRun': proof['run'], 'measurementMode': descriptions['measurementMode'],
        'asOf': datetime.datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(), 'inventorySha256': sha(inv.encode()), 'rows': rows,
        'counts': dict(collections.Counter(r['measurementStatus'] for r in rows)),
        'sameSourceTechnicalMeasurementPG3956': {'source': SOURCE, 'tests': 3716, 'suites': 545, 'physicalMain': 1643, 'nativePoints': 20, 'nativeStreams': 18,
            'remaining': proof['remaining'], 'newJUnitMethods': 2, 'acceptedLeafDelta': 0, 'physicalArtifactChanges': 0, 'newVmOperations': 0, 'formalUpdated': False,
            'F03Accepted': False, 'effortPercent': None, 'manifest': str(PROOF.relative_to(ROOT)), 'manifestSha256': sha(PROOF.read_bytes())}})
    return {NAMES[0]: texts[NAMES[0]], NAMES[1]: texts[NAMES[1]], NAMES[2]: inv, NAMES[3]: snap}


def stage():
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'clean fixed operator')
    require(not subprocess.check_output(['git', 'diff', json.loads(PROOF.read_bytes())['sourceSnapshot'], 'HEAD', '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'program/characterization'], cwd=ROOT), 'actual whole Test/Main/settings unchanged')
    before = audit.verify(); require(before['acceptedTasks'] == 17, 'current canonical audit17')
    texts = {n: (PMO / n).read_text() for n in NAMES}; proposed = candidates(texts, json.loads(PROOF.read_bytes()))
    os.umask(0o077); OUT.mkdir()
    for n in NAMES:
        (OUT / ('before-' + n)).write_text(texts[n]); (OUT / ('candidate-' + n)).write_text(proposed[n])
    result = audit.verify(master_path=OUT / ('candidate-' + NAMES[0]), budget_path=OUT / ('candidate-' + NAMES[1]), inventory_path=OUT / ('candidate-' + NAMES[2]), snapshot_path=OUT / ('candidate-' + NAMES[3]))
    require(result['acceptedTasks'] == 17, 'no new acceptance')
    record = {'actualExit': 0, 'before': {n: sha(texts[n].encode()) for n in NAMES}, 'after': {n: sha(proposed[n].encode()) for n in NAMES}, 'proofSha256': sha(PROOF.read_bytes()), 'audit': result, 'newAcceptedLeafDelta': 0}
    (OUT / 'stage.safe.json').write_text(json.dumps(record, sort_keys=True)); print(json.dumps({'actualExit': 0, 'staged': True, 'acceptedTasks': 17, 'counts': result['currentMeasurementCounts']})); return 0


def apply():
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'clean fixed apply operator')
    record = json.loads((OUT / 'stage.safe.json').read_bytes()); require(record['actualExit'] == 0 and not (OUT / 'apply-intent.safe.json').exists() and sha(PROOF.read_bytes()) == record['proofSha256'], 'one complete staged application only')
    for n in NAMES:
        require(sha((PMO / n).read_bytes()) == record['before'][n] and sha((OUT / ('candidate-' + n)).read_bytes()) == record['after'][n], 'no concurrent byte changes')
    with (OUT / 'apply-intent.safe.json').open('x') as f:
        json.dump(record, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    fd = os.open(OUT, os.O_RDONLY | os.O_DIRECTORY); os.fsync(fd); os.close(fd)
    for n in NAMES[2:]: replace_public(PMO / n, (OUT / ('candidate-' + n)).read_bytes())
    result = audit.verify(); require(result['acceptedTasks'] == 17, 'canonical after audit17')
    require(all(sha((PMO / n).read_bytes()) == record['before'][n] for n in NAMES[:2]), 'master acceptance and budget byte unchanged')
    with (OUT / 'apply.safe.json').open('x') as f: json.dump({'actualExit': 0, 'audit': result, 'proofSha256': record['proofSha256'], 'newAcceptedLeafDelta': 0}, f, sort_keys=True)
    print(json.dumps({'actualExit': 0, 'applied': True, 'acceptedTasks': 17, 'newAcceptedLeafDelta': 0})); return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=['stage', 'apply']); raise SystemExit({'stage': stage, 'apply': apply}[parser.parse_args().action]())
