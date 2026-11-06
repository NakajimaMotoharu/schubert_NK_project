"""Exact static artifact lineage; no current whole/runtime qualification is inferred."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import subprocess

r = Path.cwd()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
source = '56720d75714f60d7e31da59c3da8c02baf05de52'
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
oldp = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21766-current4217-static-artifact-lineage-v2/manifest.json'
assert sha(oldp.read_bytes()) == 'ee465df2a40a6bba40c02680062a2cbc7d0441a0bc012c67efebfb752ac70a09'
old = json.loads(oldp.read_text())
oldap = oldp.parent / 'artifacts.json'
assert sha(oldap.read_bytes()) == old['files']['artifacts.json']
prior = json.loads(oldap.read_text())
assert len(prior) == old['artifactCount'] == 1067
assert len({a['path'] for a in prior}) == 1067
held = {'RootFailedStartRecoveryTest.java', 'RootFailedStartPairRecoveryTest.java',
        'SnapshotKeyCloseWitness.java', 'pg9892_snapshot_key_close_witness.py'}
eligible = lambda p: ('/src/main/java/' in p and p.endswith('.java')) or '/src/main/resources/' in p or p.startswith('src/deployment/')
additions = {'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/InboundConsumerGroup.java': ('WBS-P005-03', source)}
previous = {a['path']: a for a in prior}
names = sorted(set(previous) | set(additions))
assert all(eligible(n) and Path(n).name not in held for n in names)
def paths_at(rev):
    data = subprocess.check_output(['git', 'ls-tree', '-r', '-z', '--name-only', rev, '--', 'src', 'program/characterization'])
    return {n for n in data.decode().split('\0') if n and eligible(n)}
tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', 'src', 'program/characterization']).decode().split('\0')
assert set(previous) == paths_at(old['source'])
assert set(names) == paths_at(source) == paths_at(head) == {n for n in tracked if eligible(n)}
assert len(names) == 1068
assert not subprocess.check_output(['git', 'diff', '--name-only', source, head, '--', *names])
raw = subprocess.check_output(['git', 'cat-file', '--batch'], input=''.join(source + ':' + n + '\n' for n in names).encode())
position = 0
current = []
changed = []
added = []
for n in names:
    end = raw.index(b'\n', position)
    header = raw[position:end].decode().split()
    assert len(header) == 3 and header[1] == 'blob'
    size = int(header[2])
    position = end + 1
    blob = raw[position:position+size]
    position += size
    assert raw[position:position+1] == b'\n'
    position += 1
    p = r / n
    assert p.is_file() and not p.is_symlink() and sha(p.read_bytes()) == sha(blob)
    if n in previous:
        a = previous[n]
        row = copy.deepcopy(a)
        row.update(previousLineage=a['lineage'],
            lineage=dict(source=old['source'], path=n, oldSha256=a['sha256'], byteChanged=sha(blob) != a['sha256'],
                domain='SAME_PATH_RESPONSIBILITY_RETAINED_NOT_ACCEPTANCE'))
        assert row['owner'] == a['owner'] and row['costOwner'] == a['costOwner']
        assert row['additionalBudgetPp'] == a['additionalBudgetPp'] == 0
        if sha(blob) != a['sha256']:
            changed.append(dict(path=n, owner=a['owner'], costOwner=a['costOwner'], kind=a['kind'],
                oldSha256=a['sha256'], currentSha256=sha(blob)))
    else:
        owner, origin = additions[n]
        assert n in paths_at(origin)
        row = dict(path=n, kind='JAVA', owner=owner, costOwner=owner, additionalBudgetPp=0,
            previousLineage=None, lineage=dict(source=old['source'], path=n, oldSha256=None,
                byteChanged=True, domain='ADDED_SUPPORT_OF_EXISTING_LEAF_NOT_ACCEPTANCE', originCommit=origin))
        added.append(dict(path=n, owner=owner, costOwner=owner, kind='JAVA', originCommit=origin,
            currentSha256=sha(blob), additionalBudgetPp=0, retrospectiveCostReallocation=False))
    row.update(sha256=sha(blob), staticSource=source, acceptance='UNASSESSED',
        qualification='UNQUALIFIED_STATIC_DESCRIPTOR_ONLY', runtimeQualificationTransferred=False,
        methodTestRequirementTrace='NOT_VERIFIED')
    current.append(row)
assert position == len(raw) and len(changed) == 4 and len(added) == 1
status = [x.split('\t') for x in subprocess.check_output(['git', 'diff', '--name-status', '--no-renames', old['source'], source, '--', *names], text=True).splitlines()]
assert {p for k, p in status if k == 'M'} == {a['path'] for a in changed}
assert {p for k, p in status if k == 'A'} == set(additions)
assert len(status) == 5 and all(k in ('A', 'M') for k, _ in status)
root_status = [x.split('\t') for x in subprocess.check_output(['git','diff','--name-status','--no-renames',old['previous']['source'],source,'--',*names],text=True).splitlines()]
assert sum(k=='M' for k,n in root_status)==27 and sum(k=='A' for k,n in root_status)==3 and len(root_status)==30
normal_refs = []
normal_inputs = {}
for name, expected, expected_java in [
    ('pg21922-consumer-stop-six-main-compile-v1', 'e925b4c24e0eff9e70f7b3fad0b595d80e90f1a444c87329215d6e4b3d5d8d1f', 967),
    ('pg21088-characterization-tool-original-main-compile-v1', '068773debc310f76f580ef1eea8de2e5735cada128d2e6c677ce62ebdffd2e0a', 5)]:
    p = r.parent / 'pgpt-runs/PG379' / name / 'manifest.safe.json'
    assert sha(p.read_bytes()) == expected
    m = json.loads(p.read_text())
    assert m['actualExit'] == 0
    inputs = {n: h for n, h in m['begin']['inputHashes'].items() if '/src/main/java/' in n and n.endswith('.java')}
    assert len(inputs) == expected_java and not (set(inputs) & set(normal_inputs))
    normal_inputs.update(inputs)
    normal_refs.append(dict(path=str(p), sha256=expected, source=m['source'], javaSources=expected_java))
java = {a['path']: a['sha256'] for a in current if '/src/main/java/' in a['path'] and a['path'].endswith('.java')}
assert java == normal_inputs and len(java) == 972
spec = r / 'evidence/01_PT/018_NK-OPS-001/3620_現56720停止fanout差分・artifact対応仕様.md'
for p in [spec, Path(__file__)]:
    assert sha(subprocess.check_output(['git', 'show', head + ':' + str(p.relative_to(r))])) == sha(p.read_bytes())
out = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21942-current56720-static-artifact-lineage-v1'
assert not out.exists()
out.mkdir()
for name, data in [('artifacts.json', current), ('changed-artifacts.json', changed), ('added-artifacts.json', added)]:
    (out / name).write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
m = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), observerSource=head,
    source=source, driverSha256=sha(Path(__file__).read_bytes()),
    specification=dict(path=str(spec.relative_to(r)), sha256=sha(spec.read_bytes())),
    previous=dict(path=str(oldp.relative_to(r)), sha256=sha(oldp.read_bytes()), source=old['source']),
    normalManifests=normal_refs, artifactCount=1068, javaSources=972,
    changedArtifacts=4, unchangedArtifacts=1063, addedArtifacts=1, removedArtifacts=0,
    ownerAndCostOwnerPreserved=True, additionalBudgetPp=0, rootLineage=dict(source=old['previous']['source'],changedArtifacts=27,addedArtifacts=3,removedArtifacts=0), dynamicRegressionStatus='PT-JMS-STOP-GROUP001..006 NOT_RUN/HOLD',
    files={n: sha((out / n).read_bytes()) for n in ['artifacts.json', 'changed-artifacts.json', 'added-artifacts.json']},
    currentWholeSourceQualified=False, exactMethodTestRequirementTraceVerified=False,
    qualifiedHistoricalCandidateModified=False, wholeG13Accepted=False, whole451Accepted=False,
    productTests=0, productInvocations=0, newMethods=0, newSourceProofs=0, newAcceptance=0,
    heldNamesExcludedBeforeIO=sorted(held), relatedBug='BUG-2407', relatedHorizontal='YKT-2152', effortRate=None)
(out / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(actualExit=0, artifacts=1068, changed=4, added=1, unchanged=1063, productTests=0,
    manifestSha256=sha((out / 'manifest.json').read_bytes()))))
