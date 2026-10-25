"""Register reviewed resource33 source primaries, not runtime acceptance or full method trace."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import trace_owner_join_resource33 as resolver
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9426-resource33-source-join-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    prior_raw=(BASE/'PG9414-reflective25-source-join-v1/manifest.json').read_bytes();assert sha(prior_raw)=='c9d1ddfbf5a0766430221a57e837278155289d39fe5c2d64b076972345125b46'
    post_raw=(BASE/'PG9424-resource33-source-post-v1/manifest.json').read_bytes();assert sha(post_raw)=='73b3eee45b6f17c32a2da075e1e8cfa5f91fdf9cd1747c1c59147d4c6ecec8a9'
    prior=json.loads(prior_raw);post=json.loads(post_raw);assert prior['source']==post['source']==SOURCE and prior['actualExit']==post['actualExit']==0
    assert post['primaryKeyKind']=='FULL_REPO_PATH' and post['catalogSha256']==resolver.CATALOG_SHA
    assert set(post['literalPrimaryOwners'])==set(resolver.DECISIONS)
    normal_raw=(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json').read_bytes();assert sha(normal_raw)=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    hashes=json.loads(normal_raw)['begin']['inputHashes'];old=prior['sourceRows'];assert len(old)==708
    inv=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes());logical={row['path']:row for row in inv['artifacts']}
    original=[dict(path=row['path'],sha256=row['sha256'],owner=row['legacyReportedOwner']) for row in old];known={row['path'] for row in old}
    for path,row in sorted(resolver.DECISIONS.items()):
        assert path not in known and path not in logical and row['owner']==row['costOwner']==post['literalPrimaryOwners'][path]
        assert row['sha256']==hashes[path]==sha((ROOT/path).read_bytes())
        original.append(dict(path=path,sha256=hashes[path],owner=None))
    rows=resolver.join_rows(original,logical,hashes,'WBS-G13.07');resolver.validate(rows,original,logical,hashes,'WBS-G13.07')
    assert len(rows)==len({row['path'] for row in rows})==741
    for before,after in zip(old,rows):
        assert all(before[k]==after[k] for k in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
        for key in ('referenceRelatedOwners','runtimeUncertainty','referenceArtifactWitnesses','artifactWitnessScope'):
            if key in before:assert before[key]==after[key]
    for row in rows[708:]:
        expected=resolver.DECISIONS[row['path']]
        assert row['canonicalOwner']==row['canonicalCostOwner']==post['literalPrimaryOwners'][row['path']]
        assert row['referenceArtifactWitnesses']==expected['reviewedArtifactWitnesses']
        assert row['runtimeUncertainty']==expected['unresolvedRuntimeReasons'] and row['referenceRelatedOwners']==expected['relatedOwners']
    rejected=[]
    for label,edit in (('cost-only',lambda v:v[708].update(canonicalCostOwner='WBS-G13.07')),('primary-forged',lambda v:v[708].update(canonicalOwner='WBS-F01')),
      ('related-forged',lambda v:v[708].update(referenceRelatedOwners=['FORGED'])),('runtime-reason-forged',lambda v:v[708].update(runtimeUncertainty=['FORGED'])),
      ('artifact-owner-forged',lambda v:v[708]['referenceArtifactWitnesses'][0].update(owner='WBS-F01')),
      ('artifact-byte-forged',lambda v:v[708]['referenceArtifactWitnesses'][0].update(sha256='0'*64)),('all-dependencies-forged',lambda v:v[708].update(artifactWitnessScope='ALL_VERIFIED')),
      ('accepted-invented',lambda v:v[708].update(ownershipStatus='ACCEPTED')),('missing',lambda v:v.pop()),('duplicate',lambda v:v.append(copy.deepcopy(v[0])))):
        changed=copy.deepcopy(rows);edit(changed);assert changed!=rows
        if label=='cost-only':assert {k for k in rows[708] if rows[708][k]!=changed[708][k]}=={'canonicalCostOwner'}
        try:resolver.validate(changed,original,logical,hashes,'WBS-G13.07')
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged resource source responsibility accepted')
    for path in resolver.DECISIONS:
        neighbor=path.removesuffix('.java')+'Foreign.java'
        assert resolver.canonical(neighbor,logical)==resolver.previous.canonical(neighbor,logical)
    sample=next(iter(resolver.DECISIONS));fixture={**logical,sample:dict(path=sample,owner='WBS-F01',costOwner='WBS-F01')}
    assert resolver.canonical(sample,fixture)['canonicalOwner']=='WBS-F01'
    universe={p for p in hashes if p.startswith('src/schubert-nk-') and p.endswith('.java') and '/java/' in p}
    registered=universe & (set(logical)|{row['path'] for row in rows});tests={p for p in universe if '/src/test/java/' in p}
    assert len(registered)==1566 and len(registered & tests)==601 and len(tests-registered)==223
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          priorManifestSha256=sha(prior_raw),independentPostSha256=sha(post_raw),catalogSha256=resolver.CATALOG_SHA,sourceRows=rows,sourceCount=741,
          previousCanonicalRelatedAndRuntimePreserved=708,newSourceOwnerCandidates=33,artifactWitnessesPreserved=True,primaryWitnessNotExhaustiveDependencies=True,
          positiveBeforeNegatives=True,metadataCounterexamples=rejected,neighbourInvariance=33,logicalBaselinePrecedenceFixture=True,
          javaPaths=1789,registered=1566,registeredMain=965,totalMain=965,registeredTest=601,totalTest=824,unregisteredTest=223,
          productTestsExecuted=0,newTestIds=0,newMain=0,newAccepted=0,coverage=None,formalUpdated=False,wholeG13Accepted=False,
          whole451Accepted=False,wholeWbsAudit='HOLD_CURRENT_SOURCE_NOT_WHOLE_QUALIFIED',effortPercent=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,registered=1566,unregistered=223,metadataNegatives=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
