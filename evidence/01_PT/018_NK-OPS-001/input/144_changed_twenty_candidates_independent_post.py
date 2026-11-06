"""Qualify candidate metadata without Product execution or acceptance inference."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import subprocess

r = Path.cwd()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
p = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21792-current4217-changed-twenty-proof-candidates-v1/manifest.json'
assert sha(p) == '8f1276f7e163392aa658cf4631e9d7a9a38b835b841f57e3dc5c5f4c115c2752'
m = load(p)
assert m['actualExit'] == 0 and m['targetCount'] == len(m['rows']) == 20 and not m['unsupported']
seed = r / m['seed']['path'] if not Path(m['seed']['path']).is_absolute() else Path(m['seed']['path'])
assert sha(seed) == m['seed']['sha256']
expected = {a['path']: a for a in load(seed) if a['kind'] == 'JAVA'}
assert set(expected) == {a['path'] for a in m['rows']} and len(expected) == 20
normal = {}
for ref in m['normalManifests']:
    q = Path(ref['path'])
    assert sha(q) == ref['sha256']
    v = load(q)
    assert v['actualExit'] == 0
    normal.update(v['begin']['inputHashes'])
assert sha(r / m['parser']['path']) == m['parser']['sha256']
held = {'RootFailedStartRecoveryTest.java', 'RootFailedStartPairRecoveryTest.java', 'SnapshotKeyCloseWitness.java', 'pg9892_snapshot_key_close_witness.py'}
refs = set()
statuses = collections.Counter()
records = 0
for row in m['rows']:
    n = row['path']
    assert Path(n).name not in held and sha(r / n) == normal[n] == row['normalMainSha256']
    assert row['canonicalOwner'] == expected[n]['owner'] and row['wholeSourceQualificationTransferred'] is False
    same = []
    for item in row['candidates']:
        q = r / item['path']
        assert q.name == 'manifest.json' and q.stat().st_size <= 2 * 1024 * 1024
        assert not any(t in held for t in q.parts) and sha(q) == item['sha256']
        v = load(q)
        assert item['source'] == v.get('source') and item['originalExit'] == v.get('actualExit')
        assert item['tests'] == v.get('tests') and item['mainPath'] == n
        cls = n.split('/src/main/java/', 1)[1][:-5]
        if item['evidenceSchema'] == 'COVERAGE_INPUT_HASHES':
            assert v['inputHashes'][n] == item['mainSha256'] and v['coverage'][cls] == item['fourCounters']
        else:
            assert item['evidenceSchema'] == 'SINGLE_TARGET_COUNTERS_BEGIN'
            assert v['begin']['targetPhysicalClasses'] == [cls]
            assert v['begin']['targetMainSourceSha256'] == item['mainSha256']
            assert v['sourcePhysicalScopeComplete'] is True and v['counters'] == item['fourCounters']
        assert item['currentMainByteEqual'] == (item['mainSha256'] == normal[n])
        assert not item['acceptanceInferred'] and not item['permissionInferred']
        cs = item['fourCounters']
        zero = lambda k: isinstance(cs.get(k), dict) and type(cs[k].get('covered')) is int and cs[k]['covered'] >= 0 and type(cs[k].get('missed')) is int and cs[k]['missed'] == 0
        three = all(zero(k) and cs[k]['covered'] > 0 for k in ['LINE', 'METHOD', 'CLASS'])
        assert item['lineMethodClassMissedZero'] == three
        assert item['allFourMissedZero'] == (three and zero('BRANCH'))
        if item['currentMainByteEqual'] and item['originalExit'] == 0:
            same.append(item)
        refs.add((item['path'], item['sha256']))
        records += 1
    full = [x for x in same if x['allFourMissedZero'] or (x['lineMethodClassMissedZero'] and x['branchAssessment'] == 'EXPLICIT_NATURAL_ZERO_NOT_BRANCH100')]
    status = 'SAME_BYTE_SUCCESS_COUNTER_CANDIDATE' if full else 'SAME_BYTE_PARTIAL_CANDIDATE' if same else 'HISTORICAL_OR_FAILED_CANDIDATE' if row['candidates'] else 'NO_SUPPORTED_SCHEMA_CANDIDATE_NOT_PROOF_OF_ABSENCE'
    assert status == row['candidateStatus']
    statuses[status] += 1
assert dict(statuses) == m['statusCounts'] == {'SAME_BYTE_SUCCESS_COUNTER_CANDIDATE': 8, 'NO_SUPPORTED_SCHEMA_CANDIDATE_NOT_PROOF_OF_ABSENCE': 12}
assert len(m['unreadBoundedManifests']) == 6
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
assert hashlib.sha256(subprocess.check_output(['git', 'show', head + ':' + str(Path(__file__).relative_to(r))])).hexdigest() == sha(Path(__file__))
out = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21794-changed-twenty-candidates-independent-post-v1'
assert not out.exists()
out.mkdir()
v = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), checkerSource=head,
    checkerSha256=sha(Path(__file__)), original=dict(path=str(p.relative_to(r)), sha256=sha(p)),
    targets=20, candidateStatusCounts=dict(statuses), distinctOriginalManifests=len(refs), candidateRecords=records,
    unreadOversize=6, unsupported=0, productTests=0, newSourceProofs=0, newAcceptance=0,
    sourceScopeCompletenessVerified=False, exactTestIdOracleSafetyVerified=False,
    wholeSourceOrPermissionInferred=False, noCandidateIsNotAbsence=True, effortRate=None)
(out / 'manifest.json').write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(actualExit=0, targets=20, candidateRecords=records, distinctOriginalManifests=len(refs), manifestSha256=sha(out / 'manifest.json'))))
