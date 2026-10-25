"""Independent Main responsibility oracle and exact-catalog guards, never target PT."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import trace_owner_join_direct_companion as resolver
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9350-direct-companion-owner-post-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
SUBJECT=BASE/'PG9348-direct-companion-owner-join-v1/manifest.json'
SUBJECT_SHA='fa2817d4f7b37d4d5cf2325edb2e1dd8b0763276fe0477805147606e86660f20'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and sha(SUBJECT.read_bytes())==SUBJECT_SHA
    value=json.loads(SUBJECT.read_bytes());assert value['source']==SOURCE and value['actualExit']==0
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']}
    old_file=BASE/'PG9334-g13-storage-residual-join-v1/manifest.json';normal_file=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'
    assert sha(old_file.read_bytes())==value['witnesses']['priorOwners'][1]=='69df39386cdb70e792f3ab31de0c050c6c465a4d9a6b0264e17f29b9d1390ffd'
    assert sha(normal_file.read_bytes())==value['witnesses']['normal'][1]=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    old=json.loads(old_file.read_bytes())['sourceRows'];known={row['path']:row for row in old}
    hashes=json.loads(normal_file.read_bytes())['begin']['inputHashes']
    catalog_file=BASE/'PG9346-direct-companion-jdk-post-v1/confirmed-candidates.json'
    assert sha(catalog_file.read_bytes())==value['catalogSha256']=='a3217e70b48808e16ccc13270d59ed7b2b3051f732acb9119dab3c93b078bc9d'
    catalog={row['path']:row for row in json.loads(catalog_file.read_bytes())};assert len(catalog)==280
    rows=value['sourceRows'];originals=value['originalInputs'];assert len(rows)==len(originals)==569
    resolver.validate(rows,originals,logical,hashes,'WBS-G13.07')
    assert {row['path'] for row in rows[289:]}==set(catalog)
    for row in rows[289:]:
        path=row['path'];main=path.replace('/src/test/java/','/src/main/java/').removesuffix('Test.java')+'.java'
        source=logical.get(main)
        expected=(source['owner'],source['costOwner']) if source is not None else (known[main]['canonicalOwner'],known[main]['canonicalCostOwner'])
        assert (row['canonicalOwner'],row['canonicalCostOwner'])==expected
        assert catalog[path]['mainPath']==main and catalog[path]['status']=='PROPOSED_CANDIDATE_REVIEW_REQUIRED_NOT_ACCEPTED'
        assert row['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED'
        assert sha((ROOT/path).read_bytes())==hashes[path]==row['sha256']==catalog[path]['sha256']
        assert sha((ROOT/main).read_bytes())==hashes[main]==catalog[path]['mainSha256']
    for before,after in zip(old,rows):assert all(before[k]==after[k] for k in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
    golden={
      'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/LayoutFieldCatalogTest.java':'WBS-P001-02',
      'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/PayloadCodecTest.java':'WBS-P002-02',
      'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/transport/BrokerTopologyTest.java':'WBS-P005-01',
      'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/BootstrapAdminServiceTest.java':'WBS-P010-05'}
    for path,expected in golden.items():
        result=resolver.canonical(path,logical);assert result['canonicalOwner']==result['canonicalCostOwner']==expected
    rejected=[]
    for label,change in (
      ('single-cost-field',lambda v:v[289].update(canonicalCostOwner='WBS-G13.07')),
      ('single-owner-field',lambda v:v[289].update(canonicalOwner='WBS-G13.07')),
      ('accepted-invented',lambda v:v[289].update(ownershipStatus='ACCEPTED')),
      ('missing',lambda v:v.pop()),('duplicate',lambda v:v.append(copy.deepcopy(v[0]))),
      ('wrong-byte',lambda v:v[289].update(sha256='0'*64))):
        changed=copy.deepcopy(rows);change(changed)
        if label=='single-cost-field':assert {k for k in rows[289] if rows[289][k]!=changed[289][k]}=={'canonicalCostOwner'}
        try:resolver.validate(changed,originals,logical,hashes,'WBS-G13.07')
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged source ownership accepted')
    for path in catalog:
        neighbour=path.removesuffix('.java')+'Foreign.java'
        assert neighbour not in catalog
        assert resolver.canonical(neighbour,logical)==resolver.previous.canonical(neighbour,logical)
    sample=next(iter(catalog));fixture={**logical,sample:dict(path=sample,owner='WBS-F02',costOwner='WBS-F02')}
    inherited=resolver.canonical(sample,fixture)
    assert inherited['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' and inherited['canonicalOwner']==inherited['canonicalCostOwner']=='WBS-F02'
    unknown='src/unclassified/Foreign.java';assert resolver.canonical(unknown,logical)['canonicalOwner'] is None
    assert value['productTestsExecuted']==value['targetClassLoading']==value['newTestIds']==value['newMain']==value['newAccepted']==0
    assert value['registered']==1394 and value['unregisteredTest']==395 and value['registeredTest']==429
    assert value['wholeG13Accepted'] is value['whole451Accepted'] is value['formalUpdated'] is False
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          joinManifestSha256=SUBJECT_SHA,catalogSha256=value['catalogSha256'],all280MainResponsibilityAndCurrentHashesVerified=True,
          previous289CanonicalPreserved=True,literalGoldenOwners=golden,metadataCounterexamples=rejected,
          positiveShapeValidatedFirst=True,costOnlyChangedField='canonicalCostOwner',neighbourRulesUnchanged=280,
          neighbourMeaning='NEW_CATALOG_RULE_INERT; EXISTING_RULES_NOT_FORCED_TO_UNKNOWN',baselinePrecedenceFixture=True,
          productTestsExecuted=0,coverage=None,formalUpdated=False,newAccepted=0,wholeG13Accepted=False,whole451Accepted=False,effortPercent=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,ownersVerified=280,neighbourInvariance=280,metadataNegatives=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
