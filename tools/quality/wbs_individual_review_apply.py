"""Apply an explicit individual review, never infer acceptance from counters.

The human-readable, hashed contract/oracle review is authoritative for semantics.
The unchanged strict WBS validator enforces evidence/source/dependency closure.
This tool changes only reviewed acceptance records, preserving before-images.
"""
import argparse
import copy
import json
from pathlib import Path
import subprocess

from pg3274_header_group_full_six import ROOT, W
from pg3282_wbs_current_source_apply import replace_public, rewrite_root
from pg3288_layout_acceptance import one_line_task
import wbs_progress_audit as audit


def require(value, message):
    if not value:
        raise ValueError(message)


def reviewed_acceptance(review, task, source, root=ROOT):
    require(review['wbs'] == task['id'] and review['productionSource'] == source
            and task['acceptance']['status'] != 'ACCEPTED', 'new same-source explicit review required')
    checks = {c['id'] for c in task['acceptanceChecks']}
    require(set(review['criteriaSatisfied']) == checks and review['reviewedBy'] and review['run'], 'all individual criteria/reviewer/run required')
    require(review['scopePaths'] == task['ownedArtifacts'] and review['requirementIds'] == task['requirementIds'], 'exact full scope/requirements required')
    require(review['evidence'] and review['expectedGeneratedFromProduction'] is False, 'independent oracle evidence required')
    proved = set()
    for item in review['evidence']:
        path = Path(item['path'])
        require(not path.is_absolute() and '..' not in path.parts and (root / path).is_file(), 'existing repository evidence required')
        require(audit.digest(root / path) == item['sha256'] and item['source'] == source
                and item['run'] and set(item['verifiedChecks']) <= checks, 'evidence hash/source/checks mismatch')
        proved.update(item['verifiedChecks'])
    require(proved == checks, 'every criterion requires explicit hashed evidence')
    return {'status': 'ACCEPTED', 'source': source, 'evidence': copy.deepcopy(review['evidence']),
            'criteriaSatisfied': list(review['criteriaSatisfied']), 'acceptedBy': review['reviewedBy']}


def main(review_path):
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'fixed clean reviews/tool required')
    review_path = review_path.resolve(); require(review_path.is_relative_to(ROOT), 'repository review required')
    before = audit.verify()
    master_path = audit.PMO / '481_PGPT詳細WBS.json'; snapshot_path = audit.PMO / '486_WBS現行実績.json'
    master = audit.read_json(master_path); snapshot = audit.read_json(snapshot_path); bundle = audit.read_json(review_path)
    require(bundle['source'] == snapshot['source'] and bundle['formalUpdated'] is False
            and bundle['wholeEffortCompletionRate'] is None and bundle['reviews'], 'no global/formal/effort claim')
    ids = [r['wbs'] for r in bundle['reviews']]; require(len(set(ids)) == len(ids), 'unique reviewed tasks required')
    rows = copy.deepcopy(snapshot['rows']); text = master_path.read_text()
    original_master = copy.deepcopy(master)
    for review in bundle['reviews']:
        task = next(t for t in master['tasks'] if t['id'] == review['wbs'])
        row = next(r for r in rows if r['id'] == task['id'])
        require(task['kind'] == 'COMPONENT' and row['measurementSource'] == bundle['source']
                and row['measurementStatus'] == 'HOST_COUNTERS_CLOSED' and all(v == 0 for v in row['missed'].values()), 'only individually reviewed closed-counter components in this tool')
        task['acceptance'] = reviewed_acceptance(review, task, bundle['source'])
        row['acceptance'] = copy.deepcopy(task['acceptance'])
        text = one_line_task(text, task['id'], task)
    # Test/source/scope/cost/criteria are not edited. Acceptance only.
    expected = copy.deepcopy(original_master)
    for task in expected['tasks']:
        task['acceptance'] = next(t['acceptance'] for t in master['tasks'] if t['id'] == task['id'])
    require(json.loads(text) == expected, 'no changes outside explicit acceptance records')
    out = W / bundle['privateSlot']; require(out.parent == W and bundle['privateSlot'].startswith('pg'), 'specific new-only private slot required')
    out.mkdir(mode=0o700)
    candidate_master = out / 'candidate-master.json'; candidate_snapshot = out / 'candidate-snapshot.json'
    candidate_master.write_text(text); candidate_snapshot.write_text(rewrite_root(snapshot_path.read_text(), {'rows': rows}))
    candidate = audit.verify(master_path=candidate_master, snapshot_path=candidate_snapshot)
    require(candidate['acceptedTasks'] == before['acceptedTasks'] + len(ids), 'exact reviewed delta required')
    for path, staged in [(master_path, candidate_master), (snapshot_path, candidate_snapshot)]:
        with (out / ('before-' + path.name)).open('xb') as stream:
            stream.write(path.read_bytes())
        replace_public(path, staged.read_bytes())
    after = audit.verify()
    value = {'actualExit': 0, 'productionSource': bundle['source'], 'reviewSha256': audit.digest(review_path),
             'acceptedIds': ids, 'acceptedBefore': before['acceptedTasks'], 'acceptedAfter': after['acceptedTasks'],
             'formalUpdated': False, 'wholeEffortCompletionRate': None, 'vmActions': 0, 'newPtCredit': 0}
    with (out / 'manifest.safe.json').open('x') as stream:
        json.dump(value, stream)
    print(json.dumps(value)); return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('review', type=Path)
    raise SystemExit(main(parser.parse_args().review))
