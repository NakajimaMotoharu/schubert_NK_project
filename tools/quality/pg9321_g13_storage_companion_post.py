"""Frozen human-reviewed spec is the owner oracle; resolver output is never its expected value."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import trace_owner_join_storage_companion as resolver
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9321-g13-storage-companion-post-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
SPEC=ROOT/'evidence/01_PT/018_NK-OPS-001/1896_G13StorageTest_直接対応19件仕様.md'
SPEC_SHA='17b9757c110952b77969aa52767ecf3b0d1c66f392c3d574365f62ea9b02770c'
SUBJECT=BASE/'PG9320-g13-storage-companion-join-v1/manifest.json'
SUBJECT_SHA='a68a1cddb4cbf42db72f8d9794170d229ac4ce2a068822694e910951adbe58bd'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    assert sha(SPEC.read_bytes())==SPEC_SHA and sha(SUBJECT.read_bytes())==SUBJECT_SHA
    expected={}
    prefix='src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/'
    for owner,names in re.findall(r'^(P[0-9-]+)：(.+)。$',SPEC.read_text(),re.MULTILINE):
        for name in names.split('、'):
            assert name.endswith('Test') and prefix+name+'.java' not in expected
            expected[prefix+name+'.java']='WBS-'+owner
    assert len(expected)==19
    value=json.loads(SUBJECT.read_bytes()); assert value['source']==SOURCE and value['actualExit']==0
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']}
    normal=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'; prior=BASE/'PG9312-g13-four-main-join-v1/manifest.json'
    assert sha(normal.read_bytes())==value['normalManifestSha256']=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    assert sha(prior.read_bytes())==value['prior260ManifestSha256']=='7fd038ec63dbf02d5f7b2d2c8b71d651a08da16b19d1bbbe518429ebe569b6b4'
    hashes=json.loads(normal.read_bytes())['begin']['inputHashes']; old=json.loads(prior.read_bytes())['sourceRows']
    rows=value['sourceRows']; originals=value['originalInputs']
    assert len(rows)==len(originals)==279
    resolver.validate(rows,originals,logical,hashes,'WBS-G13.07')
    assert {row['path'] for row in rows[260:]}==set(expected)
    for row in rows[260:]:
        main=row['path'].replace('/src/test/java/','/src/main/java/').removesuffix('Test.java')+'.java'
        assert row['canonicalOwner']==row['canonicalCostOwner']==expected[row['path']]==logical[main]['owner']==logical[main]['costOwner']
        assert row['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED'
        assert sha((ROOT/row['path']).read_bytes())==row['sha256']==hashes[row['path']]
        assert sha((ROOT/main).read_bytes())==hashes[main]
    assert len(value['companionReferences'])==19
    assert all(not row['testExecuted'] and row['testExecutionStatus']=='UNRUN_HOLD_NOT_PASS' for row in value['companionReferences'])
    for before,after in zip(old,rows):
        assert all(before[key]==after[key] for key in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
    rejected=[]
    for name,mutate in (
      ('single-cost-field-forged',lambda v:v[260].update(canonicalCostOwner='WBS-G13.07')),
      ('single-owner-field-forged',lambda v:v[260].update(canonicalOwner='WBS-G13.07')),
      ('missing-row',lambda v:v.pop()),
      ('duplicate-row',lambda v:v.append(copy.deepcopy(v[0]))),
      ('candidate-falsely-accepted',lambda v:v[260].update(ownershipStatus='ACCEPTED')),
      ('hash-forged',lambda v:v[260].update(sha256='0'*64))):
        changed=copy.deepcopy(rows); mutate(changed)
        if name=='single-cost-field-forged':assert {key for key in rows[260] if rows[260][key]!=changed[260][key]}=={'canonicalCostOwner'}
        try:resolver.validate(changed,originals,logical,hashes,'WBS-G13.07')
        except ValueError:rejected.append(name)
        else:raise AssertionError('forged companion owner accepted')
    for path in expected:
        neighbor=path.removesuffix('.java')+'Foreign.java'; result=resolver.canonical(neighbor,logical)
        assert result['ownershipStatus']=='UNKNOWN' and result['canonicalOwner'] is result['canonicalCostOwner'] is None
        rejected.append('unregistered-neighbor:'+Path(path).stem)
    assert value['testClassLoading']==value['productTestsExecuted']==value['newTestIds']==value['newMain']==value['newAccepted']==0
    assert value['javaPathDenominator']==1789 and value['explicitRegistered']==1104 and value['remainingUnregisteredTests']==685
    assert value['registeredMain']==value['totalMain']==965 and value['registeredTest']==139 and value['totalTest']==824
    assert value['wholeG13Accepted'] is value['whole451Accepted'] is value['formalUpdated'] is False
    verify(invocation); OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          joinManifestSha256=SUBJECT_SHA,frozenOracleSpecSha256=SPEC_SHA,independentGoldenOwners=expected,
          previous260CanonicalPreserved=True,metadataCounterexamples=rejected,positiveShapeValidatedFirst=True,
          costOnlyChangedField='canonicalCostOwner',testClassLoading=0,productTestsExecuted=0,coverage=None,newAccepted=0,
          wholeG13Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,golden=19,metadataCounterexamples=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
