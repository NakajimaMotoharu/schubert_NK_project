"""Exact static artifact lineage; no current whole/runtime qualification is inferred."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import subprocess

r = Path.cwd()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
source = '4217e14083c6ecac116216e08d57f4361eb2f12d'
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
oldp = r / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG15918-g13-current-static-descriptor-v1/manifest.json'
assert sha(oldp.read_bytes()) == 'b238136eb4d965b59ea281c3e610d889b18a0c102839ea9e658b2235fea6a05c'
old = json.loads(oldp.read_text())
oldap = oldp.parent / 'artifacts.json'
assert sha(oldap.read_bytes()) == old['artifactsSha256']
prior = json.loads(oldap.read_text())
assert len(prior) == old['artifactCount'] == 1065
assert len({a['path'] for a in prior}) == 1065
held = {'RootFailedStartRecoveryTest.java', 'RootFailedStartPairRecoveryTest.java',
        'SnapshotKeyCloseWitness.java', 'pg9892_snapshot_key_close_witness.py'}
eligible = lambda p: ('/src/main/java/' in p and p.endswith('.java')) or '/src/main/resources/' in p or p.startswith('src/deployment/')
names = [a['path'] for a in prior]
assert all(eligible(n) and Path(n).name not in held for n in names)
def paths_at(rev):
    data = subprocess.check_output(['git', 'ls-tree', '-r', '-z', '--name-only', rev, '--', 'src', 'program/characterization'])
    return {n for n in data.decode().split('\0') if n and eligible(n)}
tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', 'src', 'program/characterization']).decode().split('\0')
assert set(names) == paths_at(old['source']) == paths_at(source) == paths_at(head) == {n for n in tracked if eligible(n)}
assert not subprocess.check_output(['git', 'diff', '--name-only', source, head, '--', *names])
raw = subprocess.check_output(['git', 'cat-file', '--batch'], input=''.join(source + ':' + n + '\n' for n in names).encode())
position = 0
current = []
changed = []
for a in prior:
    n = a['path']
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
    row = copy.deepcopy(a)
    row.update(sha256=sha(blob), staticSource=source, acceptance='UNASSESSED',
        qualification='UNQUALIFIED_STATIC_DESCRIPTOR_ONLY', runtimeQualificationTransferred=False,
        methodTestRequirementTrace='NOT_VERIFIED', previousLineage=a['lineage'],
        lineage=dict(source=old['source'], path=n, oldSha256=a['sha256'], byteChanged=sha(blob) != a['sha256'],
            domain='SAME_PATH_RESPONSIBILITY_RETAINED_NOT_ACCEPTANCE'))
    assert row['owner'] == a['owner'] and row['costOwner'] == a['costOwner']
    assert row['additionalBudgetPp'] == a['additionalBudgetPp'] == 0
    current.append(row)
    if sha(blob) != a['sha256']:
        changed.append(dict(path=n, owner=a['owner'], costOwner=a['costOwner'], kind=a['kind'],
            oldSha256=a['sha256'], currentSha256=sha(blob)))
assert position == len(raw) and len(changed) == 25
normal_refs = []
normal_inputs = {}
for name, expected, expected_java in [
    ('pg20990-outbox-required-six-main-compile-v1', '1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618', 966),
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
assert java == normal_inputs and len(java) == 971
spec = r / 'evidence/01_PT/018_NK-OPS-001/3608_現4217静的artifact差分再束縛仕様.md'
for p in [spec, Path(__file__)]:
    assert sha(subprocess.check_output(['git', 'show', head + ':' + str(p.relative_to(r))])) == sha(p.read_bytes())
out = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21764-current4217-static-artifact-lineage-v1'
assert not out.exists()
out.mkdir()
for name, data in [('artifacts.json', current), ('changed-artifacts.json', changed)]:
    (out / name).write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
m = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), observerSource=head,
    source=source, driverSha256=sha(Path(__file__).read_bytes()),
    specification=dict(path=str(spec.relative_to(r)), sha256=sha(spec.read_bytes())),
    previous=dict(path=str(oldp.relative_to(r)), sha256=sha(oldp.read_bytes()), source=old['source']),
    normalManifests=normal_refs, artifactCount=1065, javaSources=971,
    changedArtifacts=25, unchangedArtifacts=1040, addedArtifacts=0, removedArtifacts=0,
    ownerAndCostOwnerPreserved=True, additionalBudgetPp=0,
    files={n: sha((out / n).read_bytes()) for n in ['artifacts.json', 'changed-artifacts.json']},
    currentWholeSourceQualified=False, exactMethodTestRequirementTraceVerified=False,
    qualifiedHistoricalCandidateModified=False, wholeG13Accepted=False, whole451Accepted=False,
    productTests=0, productInvocations=0, newMethods=0, newSourceProofs=0, newAcceptance=0,
    heldNamesExcludedBeforeIO=sorted(held), effortRate=None)
(out / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(actualExit=0, artifacts=1065, changed=25, unchanged=1040, productTests=0,
    manifestSha256=sha((out / 'manifest.json').read_bytes()))))
