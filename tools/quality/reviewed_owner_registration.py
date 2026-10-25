"""Register only exact independently reviewed catalogs; original owners/costs always win."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
NORMAL=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def run(library,resolver,out,prior_file,prior_sha,post_file,post_sha,expected_new,expected_registered):
    invocation=capture(library);assert not out.exists()
    assert sha(NORMAL.read_bytes())=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    prior_raw=(BASE/prior_file).read_bytes();post_raw=(BASE/post_file).read_bytes()
    assert sha(prior_raw)==prior_sha and sha(post_raw)==post_sha
    normal=json.loads(NORMAL.read_bytes());prior=json.loads(prior_raw);post=json.loads(post_raw)
    assert normal['source']==prior['source']==post['source']==SOURCE and normal['actualExit']==prior['actualExit']==post['actualExit']==0
    assert post['catalogSha256']==resolver.CATALOG_SHA
    old=prior['sourceRows'];hashes=normal['begin']['inputHashes'];known={row['path'] for row in old}
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes());logical={row['path']:row for row in inventory['artifacts']}
    original=[dict(path=row['path'],sha256=row['sha256'],owner=row['legacyReportedOwner']) for row in old]
    assert len(resolver.DECISIONS)==expected_new
    for path,row in sorted(resolver.DECISIONS.items()):
        assert path not in known and path not in logical and row['owner']==row['costOwner']==post['literalPrimaryOwners'][Path(path).stem]
        assert row['sha256']==hashes[path]==sha((ROOT/path).read_bytes())
        original.append(dict(path=path,sha256=hashes[path],owner=None))
    rows=resolver.join_rows(original,logical,hashes,'WBS-G13.07');resolver.validate(rows,original,logical,hashes,'WBS-G13.07')
    assert len(rows)==len({row['path'] for row in rows})==len(old)+expected_new
    for before,after in zip(old,rows):
        assert all(before[k]==after[k] for k in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
        for key in ('referenceRelatedOwners','runtimeUncertainty'):
            if key in before:assert before[key]==after[key]
    for row in rows[len(old):]:
        expected=resolver.DECISIONS[row['path']]
        assert row['canonicalOwner']==row['canonicalCostOwner']==expected['owner']
        assert row['referenceRelatedOwners']==expected['relatedOwners'] and row['runtimeUncertainty']==expected['unresolvedRuntimeReasons']
    index=len(old);rejected=[]
    for label,edit in (('cost-only',lambda v:v[index].update(canonicalCostOwner='WBS-G13.07')),
      ('owner-only',lambda v:v[index].update(canonicalOwner='WBS-G13.07')),('related-erased',lambda v:v[index].update(referenceRelatedOwners=[])),
      ('runtime-reason-forged',lambda v:v[index].update(runtimeUncertainty=['FORGED'])),('accepted-invented',lambda v:v[index].update(ownershipStatus='ACCEPTED')),
      ('missing',lambda v:v.pop()),('duplicate',lambda v:v.append(copy.deepcopy(v[0]))),('wrong-hash',lambda v:v[index].update(sha256='0'*64))):
        changed=copy.deepcopy(rows);edit(changed);assert changed!=rows
        if label=='cost-only':assert {k for k in rows[index] if rows[index][k]!=changed[index][k]}=={'canonicalCostOwner'}
        try:resolver.validate(changed,original,logical,hashes,'WBS-G13.07')
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged registration accepted')
    for path in resolver.DECISIONS:
        neighbor=path.removesuffix('.java')+'Foreign.java'
        assert resolver.canonical(neighbor,logical)==resolver.previous.canonical(neighbor,logical)
    sample=next(iter(resolver.DECISIONS));fixture={**logical,sample:dict(path=sample,owner='WBS-F02',costOwner='WBS-F02')}
    assert resolver.canonical(sample,fixture)['canonicalOwner']=='WBS-F02'
    universe={p for p in hashes if p.startswith('src/schubert-nk-') and p.endswith('.java') and '/java/' in p}
    registered=universe & (set(logical)|{row['path'] for row in rows});test_paths={p for p in universe if '/src/test/java/' in p}
    assert len(universe)==1789 and len(test_paths)==824 and len(registered)==expected_registered
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);out.mkdir()
    with (out/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          priorManifestSha256=prior_sha,independentPostSha256=post_sha,catalogSha256=resolver.CATALOG_SHA,sourceRows=rows,sourceCount=len(rows),
          previousCanonicalPreserved=len(old),newSourceOwnerCandidates=expected_new,relatedAndRuntimeScopesPreserved=True,
          positiveBeforeNegatives=True,metadataCounterexamples=rejected,neighbourInvariance=expected_new,
          javaPaths=1789,registered=expected_registered,registeredMain=965,totalMain=965,registeredTest=len(registered & test_paths),
          totalTest=824,unregisteredTest=len(test_paths-registered),productTestsExecuted=0,newTestIds=0,newMain=0,newAccepted=0,coverage=None,
          formalUpdated=False,wholeG13Accepted=False,whole451Accepted=False,wholeWbsAudit='HOLD_CURRENT_SOURCE_NOT_WHOLE_QUALIFIED',effortPercent=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,registered=expected_registered,newCandidates=expected_new,unregistered=len(test_paths-registered),
      metadataNegatives=len(rejected),manifestSha256=sha((out/'manifest.json').read_bytes()))))
