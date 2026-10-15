"""Apply F01 policy-document review only; never accept code or pending F03 gates."""
import argparse
import copy
import json
import os
from pathlib import Path
import subprocess

import wbs_progress_audit as audit
from wbs_individual_review_apply import ROOT, W, require, reviewed_acceptance
from pg3282_wbs_current_source_apply import replace_public, rewrite_root
from pg3288_layout_acceptance import one_line_task


def document_eligible(task, row, proof, source):
    require(task['id'] == row['id'] == 'WBS-F01' and task['kind'] == 'FOUNDATION', 'F01 policy only; no other foundation/code acceptance')
    require(task['ownedArtifacts'] == [] and task['requirementIds'] == []
            and row['measurementStatus'] == 'ARTIFACT_CONFIRMED' and 'measuredFamilies' not in row,
            'non-executable policy scope only, no Java counter exclusion')
    require(proof['productionSource'] == source and proof['actualExit'] == 0
            and proof['coverageApplicability'] == 'NON_EXECUTABLE_POLICY_DOCUMENT'
            and proof['javaCoverageExcluded'] is False and proof['F03Accepted'] is False
            and proof['formalUpdated'] is False and proof['wholeEffortCompletionRate'] is None,
            'no execution/global/F03/effort claim')
    require(proof['policySections'] == [str(i) for i in range(1, 15)]
            and set(proof['productionModules']) == {'protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'}
            and proof['separateCompatibilityModule'] == 'program/characterization'
            and proof['allSevenPomHashesEqualA9'] is True, 'exact reviewed full policy/module scope')


def main(path):
    os.umask(0o077)
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'fixed clean review and proof required')
    path = path.resolve(); require(path.is_relative_to(ROOT), 'repository review')
    bundle = audit.read_json(path); require(len(bundle['reviews']) == 1 and bundle['formalUpdated'] is False
            and bundle['wholeEffortCompletionRate'] is None, 'one explicit policy review only')
    before = audit.verify(); master_path = audit.PMO / '481_PGPT詳細WBS.json'; snapshot_path = audit.PMO / '486_WBS現行実績.json'
    master = audit.read_json(master_path); snapshot = audit.read_json(snapshot_path)
    require(bundle['source'] == snapshot['source'], 'same current source')
    task = next(t for t in master['tasks'] if t['id'] == 'WBS-F01'); rows = copy.deepcopy(snapshot['rows'])
    row = next(r for r in rows if r['id'] == task['id']); review = bundle['reviews'][0]
    proof_relative = Path(bundle['policyProof']['path'])
    require(not proof_relative.is_absolute() and '..' not in proof_relative.parts, 'repository-relative proof only')
    proof_path = ROOT / proof_relative
    require(proof_path.resolve().is_relative_to(ROOT), 'no proof symlink escape')
    require(proof_path.is_file() and audit.digest(proof_path) == bundle['policyProof']['sha256'], 'fixed actual policy proof')
    proof = audit.read_json(proof_path); document_eligible(task, row, proof, bundle['source'])
    for p, digest in {**proof['documentSha256'], **proof['pomSha256']}.items():
        require(not Path(p).is_absolute() and '..' not in Path(p).parts
                and (ROOT / p).resolve().is_relative_to(ROOT), 'repository document/POM only')
        require(audit.digest(ROOT / p) == digest, 'actual current document/POM unchanged')
    original = copy.deepcopy(master)
    task['acceptance'] = reviewed_acceptance(review, task, bundle['source']); row['acceptance'] = copy.deepcopy(task['acceptance'])
    text = one_line_task(master_path.read_text(), task['id'], task)
    for item in original['tasks']:
        if item['id'] == task['id']:item['acceptance'] = copy.deepcopy(task['acceptance'])
    require(json.loads(text) == original, 'no scope/cost/criteria/source mutation')
    out = W / bundle['privateSlot']; require(out.parent == W and bundle['privateSlot'].startswith('pg'), 'specific new-only slot')
    out.mkdir(mode=0o700); candidate_master = out / 'candidate-master.json'; candidate_snapshot = out / 'candidate-snapshot.json'
    candidate_master.write_text(text); candidate_snapshot.write_text(rewrite_root(snapshot_path.read_text(), {'rows': rows}))
    candidate = audit.verify(master_path=candidate_master, snapshot_path=candidate_snapshot)
    require(candidate['acceptedTasks'] == before['acceptedTasks'] + 1, 'exact policy-only delta')
    for dest, staged in [(master_path, candidate_master), (snapshot_path, candidate_snapshot)]:
        with (out / ('before-' + dest.name)).open('xb') as stream:stream.write(dest.read_bytes())
        replace_public(dest, staged.read_bytes())
    after = audit.verify()
    value = {'actualExit': 0, 'productionSource': bundle['source'], 'reviewSha256': audit.digest(path),
             'acceptedIds': ['WBS-F01'], 'acceptedBefore': before['acceptedTasks'], 'acceptedAfter': after['acceptedTasks'],
             'F03Accepted': False, 'formalUpdated': False, 'wholeEffortCompletionRate': None, 'newPtCredit': 0}
    with (out / 'manifest.safe.json').open('x') as stream:json.dump(value, stream)
    print(json.dumps(value)); return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('review', type=Path)
    raise SystemExit(main(parser.parse_args().review))
