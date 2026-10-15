"""Apply explicit C04-only non-Java configuration review, never relax Java/static gates."""
import argparse
import copy
from collections import Counter
import json
import os
from pathlib import Path
import subprocess

import wbs_progress_audit as audit
from wbs_individual_review_apply import ROOT, W, require, reviewed_acceptance
from pg3282_wbs_current_source_apply import replace_public, rewrite_root
from pg3288_layout_acceptance import one_line_task

CONFIG = 'src/deployment/artemis/etc/broker.xml'


def eligible(task, row, proof, source):
    require(task['id'] == row['id'] == 'WBS-C04' and task['kind'] == 'CONFIG'
            and task['ownedArtifacts'] == [CONFIG] and task['sharedClassReferences'] == []
            and task['dependencies'] == [] and not task.get('children'), 'specific complete independent config scope')
    require('measuredFamilies' not in row, 'no executable Java counter exclusion')
    require(proof['actualExit'] == 0 and proof['productionSource'] == source and proof['ownedArtifact'] == CONFIG
            and proof['formalUpdated'] is False and proof['effortCompletionRate'] is None
            and proof['runtimeBrokerStarted'] is False and proof['newProductionPtCredit'] == 0, 'no scope/formal inflation')
    require(proof['requirementIds'] == task['requirementIds'], 'all actual requirement ownership')
    x = proof['wholeActualOriginal']
    require(x['tests'] == len(x['cases']) == 4 and x['failures'] == x['errors'] == x['skipped'] == 0
            and all(not c['nonSuccessElements'] for c in x['cases']), 'actual original four successful cases')
    require(x['brokerInputSha256'] == x['brokerActualSha256'] == proof['artifactSha256'], 'fixed actual source input')
    n = proof['schemaCanary']
    require(n['compileExit'] == n['actualExit'] == 0 and n['originalAcceptedBeforeAndAfter'] is True
            and n['independentInvalidFourRejected'] is True, 'independent official schema canaries')
    require(proof['independentPolicy'] == {'globalFields': 24, 'addresses': 6, 'policyFieldsEach': 26,
            'aclMatches': 13, 'independentSemanticNegatives': 3, 'allRefused': True}, 'all literal policy/negative scope')


def main(review_path):
    os.umask(0o077)
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'clean fixed review required')
    review_path = review_path.resolve(); require(review_path.is_relative_to(ROOT), 'repository review')
    bundle = audit.read_json(review_path); require(len(bundle['reviews']) == 1 and bundle['formalUpdated'] is False
            and bundle['wholeEffortCompletionRate'] is None, 'one reviewed config only')
    before = audit.verify(); master_path = audit.PMO / '481_PGPT詳細WBS.json'; snapshot_path = audit.PMO / '486_WBS現行実績.json'
    master = audit.read_json(master_path); snapshot = audit.read_json(snapshot_path)
    require(snapshot['source'] == bundle['source'], 'same physical measurement source')
    task = next(t for t in master['tasks'] if t['id'] == 'WBS-C04'); rows = copy.deepcopy(snapshot['rows'])
    row = next(r for r in rows if r['id'] == task['id']); original_master = copy.deepcopy(master)
    relative = Path(bundle['configurationProof']['path'])
    require(not relative.is_absolute() and '..' not in relative.parts and (ROOT / relative).resolve().is_relative_to(ROOT), 'repository proof no escape')
    path = ROOT / relative; require(audit.digest(path) == bundle['configurationProof']['sha256'], 'fixed complete proof')
    proof = audit.read_json(path); eligible(task, row, proof, bundle['source'])
    require(audit.digest(ROOT / CONFIG) == proof['artifactSha256'], 'current artifact unchanged')
    for p, h in proof['documentSha256'].items():
        require(not Path(p).is_absolute() and '..' not in Path(p).parts and (ROOT / p).resolve().is_relative_to(ROOT), 'repository source document')
        require(audit.digest(ROOT / p) == h, 'reviewed canonical text unchanged')
    task['acceptance'] = reviewed_acceptance(bundle['reviews'][0], task, bundle['source'])
    row['acceptance'] = copy.deepcopy(task['acceptance']); row['measurementStatus'] = 'ARTIFACT_CONFIRMED'
    row['configurationVerification'] = {'source': bundle['source'], 'run': proof['run'], 'path': str(relative), 'sha256': audit.digest(path)}
    row['evidence'] = list(dict.fromkeys(row['evidence'] + [str(relative)]))
    text = one_line_task(master_path.read_text(), task['id'], task)
    expected = copy.deepcopy(original_master)
    next(t for t in expected['tasks'] if t['id'] == task['id'])['acceptance'] = copy.deepcopy(task['acceptance'])
    require(json.loads(text) == expected, 'no cost/scope/criteria/Java changes')
    out = W / bundle['privateSlot']; require(out.parent == W and bundle['privateSlot'].startswith('pg'), 'specific new-only slot')
    out.mkdir(mode=0o700)
    cm, cs = out / 'candidate-master.json', out / 'candidate-snapshot.json'
    cm.write_text(text); cs.write_text(rewrite_root(snapshot_path.read_text(), {'rows': rows, 'counts': dict(Counter(r['measurementStatus'] for r in rows))}))
    candidate = audit.verify(master_path=cm, snapshot_path=cs)
    require(candidate['acceptedTasks'] == before['acceptedTasks'] + 1, 'exact one reviewed delta')
    for destination, staged in [(master_path, cm), (snapshot_path, cs)]:
        with (out / ('before-' + destination.name)).open('xb') as f:
            f.write(destination.read_bytes())
        replace_public(destination, staged.read_bytes())
    after = audit.verify()
    value = {'actualExit': 0, 'productionSource': bundle['source'], 'reviewSha256': audit.digest(review_path),
             'acceptedIds': ['WBS-C04'], 'acceptedBefore': before['acceptedTasks'], 'acceptedAfter': after['acceptedTasks'],
             'javaCounterClassificationUnchanged': True, 'formalUpdated': False, 'wholeEffortCompletionRate': None, 'newPtCredit': 0}
    with (out / 'manifest.safe.json').open('x') as f:
        json.dump(value, f)
    print(json.dumps(value))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('review', type=Path)
    main(parser.parse_args().review)
