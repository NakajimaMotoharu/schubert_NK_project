"""Independent frozen responsibility table oracle; helper paths are not executed tests."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import trace_owner_join_storage_residual as resolver
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9336-g13-storage-residual-post-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
SUBJECT=BASE/'PG9334-g13-storage-residual-join-v1/manifest.json'
SUBJECT_SHA='69df39386cdb70e792f3ab31de0c050c6c465a4d9a6b0264e17f29b9d1390ffd'
SPEC=ROOT/'evidence/01_PT/018_NK-OPS-001/1900_G13StorageResidual_残10path責任対応仕様.md'
SPEC_SHA='a1cffb354099c85e2649d80b4068f82d95a2c9d2d76567ae99058b0ef2460144'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    assert sha(SUBJECT.read_bytes())==SUBJECT_SHA and sha(SPEC.read_bytes())==SPEC_SHA
    value=json.loads(SUBJECT.read_bytes());assert value['source']==SOURCE and value['actualExit']==0
    table=re.findall(r'^\|([A-Za-z]+)\|([A-Za-z]+)\|(WBS-P[0-9-]+)\|(TEST(?:_HELPER)?)\|$',SPEC.read_text(),re.MULTILINE)
    expected={name:(main,owner,kind) for name,main,owner,kind in table};assert len(expected)==len(table)==10
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']}
    normal=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json';prior=BASE/'PG9320-g13-storage-companion-join-v1/manifest.json'
    assert sha(normal.read_bytes())==value['normalManifestSha256']=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    assert sha(prior.read_bytes())==value['prior279ManifestSha256']=='a68a1cddb4cbf42db72f8d9794170d229ac4ce2a068822694e910951adbe58bd'
    hashes=json.loads(normal.read_bytes())['begin']['inputHashes'];old=json.loads(prior.read_bytes())['sourceRows']
    rows=value['sourceRows'];originals=value['originalInputs'];assert len(rows)==len(originals)==289
    resolver.validate(rows,originals,logical,hashes,'WBS-G13.07')
    by_name={Path(row['path']).stem:row for row in rows[279:]}
    assert set(by_name)==set(expected)
    relationships={Path(row['path']).stem:row for row in value['relationships']};assert len(relationships)==10
    for name,(main,owner,kind) in expected.items():
        row=by_name[name];related=relationships[name]
        assert row['canonicalOwner']==row['canonicalCostOwner']==owner
        assert row['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED'
        main_path=row['path'].replace('/src/test/java/','/src/main/java/').rsplit('/',1)[0]+'/'+main+'.java'
        assert logical[main_path]['owner']==logical[main_path]['costOwner']==owner
        assert related['mainPath']==main_path and related['kind']==kind and related['testExecuted'] is False
        assert sha((ROOT/row['path']).read_bytes())==row['sha256']==hashes[row['path']]
        if kind=='TEST_HELPER':assert related['driverTest'] is not None
        else:assert related['driverTest'] is None
    for before,after in zip(old,rows):assert all(before[k]==after[k] for k in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
    rejected=[]
    for label,change in (
      ('single-cost-field',lambda v:v[279].update(canonicalCostOwner='WBS-G13.07')),
      ('single-owner-field',lambda v:v[279].update(canonicalOwner='WBS-G13.07')),
      ('candidate-falsely-accepted',lambda v:v[279].update(ownershipStatus='ACCEPTED')),
      ('missing',lambda v:v.pop()),('duplicate',lambda v:v.append(copy.deepcopy(v[0]))),
      ('wrong-byte',lambda v:v[279].update(sha256='0'*64))):
        mutated=copy.deepcopy(rows);change(mutated)
        if label=='single-cost-field':assert {k for k in rows[279] if rows[279][k]!=mutated[279][k]}=={'canonicalCostOwner'}
        try:resolver.validate(mutated,originals,logical,hashes,'WBS-G13.07')
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged metadata accepted')
    for name in expected:
        unknown=resolver.canonical(resolver.PREFIX+name+'Foreign.java',logical)
        assert unknown['canonicalOwner'] is unknown['canonicalCostOwner'] is None and unknown['ownershipStatus']=='UNKNOWN'
        rejected.append('unregistered-neighbor:'+name)
    assert value['productTestsExecuted']==value['testClassLoading']==value['newTestIds']==value['newMain']==value['newAccepted']==0
    assert value['registered']==1114 and value['unregisteredTest']==675 and value['registeredTest']==149
    assert value['newTestOwners']==8 and value['newHelperOwners']==2 and value['storageTestSourceRegistered']==value['storageTestSourceTotal']==29
    assert value['wholeG13Accepted'] is value['whole451Accepted'] is value['formalUpdated'] is False
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          joinManifestSha256=SUBJECT_SHA,oracleSpecSha256=SPEC_SHA,independentResponsibilityTable=table,
          metadataCounterexamples=rejected,positiveShapeValidatedFirst=True,costOnlyChangedField='canonicalCostOwner',
          previous279Preserved=True,eightTestsTwoHelpers=True,productTestsExecuted=0,testClassLoading=0,
          coverage=None,formalUpdated=False,newAccepted=0,effortPercent=None,wholeG13Accepted=False,whole451Accepted=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,golden=10,metadataCounterexamples=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
