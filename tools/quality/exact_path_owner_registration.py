"""Full-path literal catalog registration, including empty related sets and retained runtime holds."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def run(library,resolver,out,prior_name,prior_sha,post_name,post_sha,count,expected_registered):
    invocation=capture(library);assert not out.exists()
    prior_raw=(BASE/prior_name).read_bytes();post_raw=(BASE/post_name).read_bytes()
    assert sha(prior_raw)==prior_sha and sha(post_raw)==post_sha
    prior=json.loads(prior_raw);post=json.loads(post_raw)
    assert prior['source']==post['source']==SOURCE and prior['actualExit']==post['actualExit']==0
    assert post['primaryKeyKind']=='FULL_REPO_PATH' and post['catalogSha256']==resolver.CATALOG_SHA
    assert set(post['literalPrimaryOwners'])==set(resolver.DECISIONS) and len(resolver.DECISIONS)==count
    normal_raw=(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json').read_bytes()
    assert sha(normal_raw)=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    hashes=json.loads(normal_raw)['begin']['inputHashes'];old=prior['sourceRows']
    inv=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes());logical={row['path']:row for row in inv['artifacts']}
    original=[dict(path=row['path'],sha256=row['sha256'],owner=row['legacyReportedOwner']) for row in old];known={row['path'] for row in old}
    for path,row in sorted(resolver.DECISIONS.items()):
        assert path not in known and path not in logical
        assert row['owner']==row['costOwner']==post['literalPrimaryOwners'][path]
        assert row['sha256']==hashes[path]==sha((ROOT/path).read_bytes())
        original.append(dict(path=path,sha256=hashes[path],owner=None))
    rows=resolver.join_rows(original,logical,hashes,'WBS-G13.07');resolver.validate(rows,original,logical,hashes,'WBS-G13.07')
    assert len(rows)==len({row['path'] for row in rows})==len(old)+count
    for before,after in zip(old,rows):
        assert all(before[k]==after[k] for k in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
        for key in ('referenceRelatedOwners','runtimeUncertainty'):
            if key in before:assert before[key]==after[key]
    for row in rows[len(old):]:
        expected=resolver.DECISIONS[row['path']]
        assert row['canonicalOwner']==row['canonicalCostOwner']==post['literalPrimaryOwners'][row['path']]
        assert row['referenceRelatedOwners']==expected['relatedOwners'] and row['runtimeUncertainty']==expected['unresolvedRuntimeReasons']
    index=len(old);rejected=[]
    for label,edit in (('cost-only',lambda v:v[index].update(canonicalCostOwner='WBS-G13.07')),('primary-only',lambda v:v[index].update(canonicalOwner='WBS-G13.07')),
      ('related-forged',lambda v:v[index].update(referenceRelatedOwners=['FORGED'])),('runtime-hold-erased',lambda v:v[index].update(runtimeUncertainty=[])),
      ('accepted-forged',lambda v:v[index].update(ownershipStatus='ACCEPTED')),('missing',lambda v:v.pop()),
      ('duplicate',lambda v:v.append(copy.deepcopy(v[0]))),('wrong-byte',lambda v:v[index].update(sha256='0'*64))):
        changed=copy.deepcopy(rows);edit(changed);assert changed!=rows
        if label=='cost-only':assert {k for k in rows[index] if rows[index][k]!=changed[index][k]}=={'canonicalCostOwner'}
        try:resolver.validate(changed,original,logical,hashes,'WBS-G13.07')
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged path ownership/runtime qualification accepted')
    for path in resolver.DECISIONS:
        neighbor=path.removesuffix('.java')+'Foreign.java'
        assert resolver.canonical(neighbor,logical)==resolver.previous.canonical(neighbor,logical)
    api_same_name='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/config/BrokerGraph334Test.java'
    assert api_same_name not in resolver.DECISIONS and resolver.canonical(api_same_name,logical)==resolver.previous.canonical(api_same_name,logical)
    sample=next(iter(resolver.DECISIONS));fixture={**logical,sample:dict(path=sample,owner='WBS-F02',costOwner='WBS-F02')}
    assert resolver.canonical(sample,fixture)['canonicalOwner']=='WBS-F02'
    universe={p for p in hashes if p.startswith('src/schubert-nk-') and p.endswith('.java') and '/java/' in p}
    registered=universe & (set(logical)|{row['path'] for row in rows});tests={p for p in universe if '/src/test/java/' in p}
    assert len(universe)==1789 and len(tests)==824 and len(registered)==expected_registered
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);out.mkdir()
    with (out/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          priorManifestSha256=prior_sha,independentPostSha256=post_sha,catalogSha256=resolver.CATALOG_SHA,sourceRows=rows,sourceCount=len(rows),
          previousCanonicalPreserved=len(old),newSourceOwnerCandidates=count,fullRepoPathPrimaryKeys=True,runtimeHoldsPreserved=True,
          positiveBeforeNegatives=True,metadataCounterexamples=rejected,neighbourInvariance=count,apiSameNameRuleUnchanged=True,
          javaPaths=1789,registered=expected_registered,registeredMain=965,totalMain=965,registeredTest=len(registered & tests),totalTest=824,
          unregisteredTest=len(tests-registered),productTestsExecuted=0,newTestIds=0,newMain=0,newAccepted=0,coverage=None,
          formalUpdated=False,wholeG13Accepted=False,whole451Accepted=False,wholeWbsAudit='HOLD_CURRENT_SOURCE_NOT_WHOLE_QUALIFIED',effortPercent=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,registered=expected_registered,newCandidates=count,unregistered=len(tests-registered),
      metadataNegatives=len(rejected),manifestSha256=sha((out/'manifest.json').read_bytes()))))
