"""Literal independent two-responsibility oracle and exact-neighbour/cost counterexamples."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import trace_owner_join_inherited_companion as resolver
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9376-inherited-companion-post-v1'
SUBJECT=BASE/'PG9374-inherited-companion-join-v1/manifest.json'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
SUBJECT_SHA='0f2cfc89eb1750dd6a6ba220a721554ee6388c5441aec6775e40028b5dd0d0aa'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and sha(SUBJECT.read_bytes())==SUBJECT_SHA
    value=json.loads(SUBJECT.read_bytes());assert value['source']==SOURCE and value['actualExit']==0
    prefix='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/'
    oracle={prefix+'file/MorningCurrentInvalidationTest.java':('WBS-P018-03','MorningCurrentInvalidation$Store','invalidate'),
      prefix+'platform/MorningPreviousBrokerTest.java':('WBS-P017-10','MorningPreviousBroker$Query','read')}
    normal_path=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json';prior_path=BASE/'PG9364-static-companion-owner-join-v1/manifest.json'
    assert sha(normal_path.read_bytes())==value['normalManifestSha256']=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    assert sha(prior_path.read_bytes())==value['priorManifestSha256']=='5f7b552fb08fb96e388232952ab88ac61d70a581176c1e63400b405da864cbbb'
    hashes=json.loads(normal_path.read_bytes())['begin']['inputHashes'];old=json.loads(prior_path.read_bytes())['sourceRows']
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']};known={row['path']:row for row in old}
    rows=value['sourceRows'];originals=value['originalInputs']
    resolver.validate(rows,originals,logical,hashes,'WBS-G13.07')
    assert len(rows)==626 and {row['path'] for row in rows[624:]}==set(oracle)
    evidence={row['path']:row for row in value['interfaceEvidence']};assert set(evidence)==set(oracle)
    for row in rows[624:]:
        path=row['path'];owner,interface,method=oracle[path];proof=evidence[path]
        main=path.replace('/src/test/java/','/src/main/java/').removesuffix('Test.java')+'.java'
        baseline=logical.get(main);actual=(baseline['owner'],baseline['costOwner']) if baseline else (known[main]['canonicalOwner'],known[main]['canonicalCostOwner'])
        assert (row['canonicalOwner'],row['canonicalCostOwner'])==actual==(owner,owner)
        assert proof['interfaceClass'].endswith('.'+interface) and proof['javapActualExit']==0
        assert any(' '+method+'(' in line for line in proof['interfaceDeclarations'])
        assert proof['mainPath']==main and row['sha256']==hashes[path]==sha((ROOT/path).read_bytes())
        assert proof['mainSha256']==hashes[main]==sha((ROOT/main).read_bytes())
    for before,after in zip(old,rows):assert all(before[k]==after[k] for k in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
    rejected=[]
    for label,change in (('cost-only',lambda v:v[624].update(canonicalCostOwner='WBS-G13.07')),
      ('owner-only',lambda v:v[624].update(canonicalOwner='WBS-G13.07')),('forged-pass',lambda v:v[624].update(ownershipStatus='ACCEPTED')),
      ('missing',lambda v:v.pop()),('duplicate',lambda v:v.append(copy.deepcopy(v[0]))),('wrong-hash',lambda v:v[624].update(sha256='0'*64))):
        changed=copy.deepcopy(rows);change(changed)
        if label=='cost-only':assert {k for k in rows[624] if rows[624][k]!=changed[624][k]}=={'canonicalCostOwner'}
        try:resolver.validate(changed,originals,logical,hashes,'WBS-G13.07')
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged responsibility accepted')
    for path in oracle:
        neighbor=path.removesuffix('.java')+'Foreign.java'
        assert resolver.canonical(neighbor,logical)==resolver.previous.canonical(neighbor,logical)
    sample=next(iter(oracle));fixture={**logical,sample:dict(path=sample,owner='WBS-F02',costOwner='WBS-F02')}
    assert resolver.canonical(sample,fixture)['canonicalOwner']=='WBS-F02'
    assert value['registered']==1451 and value['registeredTest']==486 and value['unregisteredTest']==338
    assert value['productTestsExecuted']==value['targetCompile']==value['targetClassLoading']==value['newTestIds']==value['newMain']==value['newAccepted']==0
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          joinManifestSha256=SUBJECT_SHA,literalResponsibilitiesVerified=2,previous624CanonicalPreserved=True,
          positiveShapeBeforeCounterexamples=True,metadataCounterexamples=rejected,neighbourRuleInvariance=2,
          logicalBaselinePrecedenceFixture=True,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,literalResponsibilities=2,metadataNegatives=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
