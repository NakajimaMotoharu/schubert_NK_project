"""Independent responsibility/byte/source witness join; exact membership only, not PT."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import trace_owner_join_static_companion as resolver
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9366-static-companion-owner-post-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
SUBJECT=BASE/'PG9364-static-companion-owner-join-v1/manifest.json'
SUBJECT_SHA='5f7b552fb08fb96e388232952ab88ac61d70a581176c1e63400b405da864cbbb'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and sha(SUBJECT.read_bytes())==SUBJECT_SHA
    value=json.loads(SUBJECT.read_bytes());assert value['source']==SOURCE and value['actualExit']==0
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']}
    prior_path=BASE/'PG9348-direct-companion-owner-join-v1/manifest.json';normal_path=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'
    assert sha(prior_path.read_bytes())==value['witnesses']['prior'][1]=='fa2817d4f7b37d4d5cf2325edb2e1dd8b0763276fe0477805147606e86660f20'
    assert sha(normal_path.read_bytes())==value['witnesses']['normal'][1]=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    old=json.loads(prior_path.read_bytes())['sourceRows'];known={row['path']:row for row in old}
    hashes=json.loads(normal_path.read_bytes())['begin']['inputHashes']
    evidence_path=BASE/'PG9362-static-companion-asm-v1/manifest.json'
    assert sha(evidence_path.read_bytes())==value['witnesses']['asm'][1]=='5a98abbe4cf6ddbaf7259b72c6b68996e46f5feaeaaba51455756f5d1d53ff37'
    evidence=json.loads(evidence_path.read_bytes());catalog_path=evidence_path.parent/'confirmed-candidates.json'
    assert sha(catalog_path.read_bytes())==evidence['confirmedSha256']==value['catalogSha256']=='7f330ff0019011d31582fa98506ebdaa84c78afb891e156200110ef60fa03b03'
    proof_path=evidence_path.parent/'class-proofs.json';assert sha(proof_path.read_bytes())==evidence['proofsSha256']
    proofs={row['classPath']:row for row in json.loads(proof_path.read_bytes())}
    catalog={row['path']:row for row in json.loads(catalog_path.read_bytes())};assert len(catalog)==55
    rows=value['sourceRows'];originals=value['originalInputs'];assert len(rows)==len(originals)==624
    resolver.validate(rows,originals,logical,hashes,'WBS-G13.07');assert {row['path'] for row in rows[569:]}==set(catalog)
    for row in rows[569:]:
        path=row['path'];item=catalog[path];main=path.replace('/src/test/java/','/src/main/java/').removesuffix('Test.java')+'.java'
        expected=(logical[main]['owner'],logical[main]['costOwner']) if main in logical else (known[main]['canonicalOwner'],known[main]['canonicalCostOwner'])
        assert (row['canonicalOwner'],row['canonicalCostOwner'])==expected and item['mainPath']==main
        assert row['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED'
        assert sha((ROOT/path).read_bytes())==hashes[path]==row['sha256']==item['sha256']
        assert sha((ROOT/main).read_bytes())==hashes[main]==item['mainSha256']
        assert item['witnessClasses']
        for witness in item['witnessClasses']:
            proof=proofs[witness]
            assert proof['testPath']==path and proof['mainPath']==main and proof['referenceConfirmed'] is True
            assert proof['sourceFile']==Path(path).name and proof['confirmedOwners']
            assert set(proof['confirmedOwners']) <= set(proof['sourceBoundMainOwners']) & set(proof['independentJavapOwners'])
    for before,after in zip(old,rows):assert all(before[k]==after[k] for k in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
    rejected=[]
    for label,change in (
      ('single-cost-field',lambda v:v[569].update(canonicalCostOwner='WBS-G13.07')),
      ('single-owner-field',lambda v:v[569].update(canonicalOwner='WBS-G13.07')),
      ('accepted-invented',lambda v:v[569].update(ownershipStatus='ACCEPTED')),
      ('missing',lambda v:v.pop()),('duplicate',lambda v:v.append(copy.deepcopy(v[0]))),
      ('wrong-byte',lambda v:v[569].update(sha256='0'*64))):
        changed=copy.deepcopy(rows);change(changed)
        if label=='single-cost-field':assert {k for k in rows[569] if rows[569][k]!=changed[569][k]}=={'canonicalCostOwner'}
        try:resolver.validate(changed,originals,logical,hashes,'WBS-G13.07')
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged source responsibility accepted')
    for path in catalog:
        neighbor=path.removesuffix('.java')+'Foreign.java'
        assert neighbor not in catalog and resolver.canonical(neighbor,logical)==resolver.previous.canonical(neighbor,logical)
    sample=next(iter(catalog));fixture={**logical,sample:dict(path=sample,owner='WBS-F02',costOwner='WBS-F02')}
    baseline=resolver.canonical(sample,fixture);assert baseline['canonicalOwner']==baseline['canonicalCostOwner']=='WBS-F02'
    assert baseline['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE'
    assert value['registered']==1449 and value['registeredTest']==484 and value['unregisteredTest']==340
    assert value['productTestsExecuted']==value['newTestIds']==value['newMain']==value['newAccepted']==0
    assert value['wholeG13Accepted'] is value['whole451Accepted'] is value['formalUpdated'] is False
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          joinManifestSha256=SUBJECT_SHA,catalogSha256=value['catalogSha256'],all55ResponsibilitiesAndActualCodeWitnessesVerified=True,
          previous569CanonicalPreserved=True,metadataCounterexamples=rejected,positiveShapeValidatedFirst=True,
          costOnlyChangedField='canonicalCostOwner',neighbourRuleInvariance=55,baselinePrecedenceFixture=True,
          productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,wholeG13Accepted=False,whole451Accepted=False,effortPercent=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,ownersVerified=55,metadataNegatives=len(rejected),neighbourInvariance=55,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
