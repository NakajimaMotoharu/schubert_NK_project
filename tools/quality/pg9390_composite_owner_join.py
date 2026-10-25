"""Commit finite reviewed source primary responsibilities; no functional PT or effort claim."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import trace_owner_join_composite_reference as resolver
from pg9388_composite_reference_post import ORACLE,short
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9390-composite-owner-join-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    pins={
      'normal':('PG9246-web-life-lock-six-compile-v1/manifest.json','989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'),
      'prior':('PG9374-inherited-companion-join-v1/manifest.json','0f2cfc89eb1750dd6a6ba220a721554ee6388c5441aec6775e40028b5dd0d0aa'),
      'graph':('PG9386-composite-reference-graph-v3/manifest.json','3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15'),
      'post':('PG9388-composite-reference-post-v1/manifest.json','46d1cf32bc0e7ec1ac5882f43250201eb6d23e72acb4c6ef64cea823d9f1087e')}
    proofs={}
    for key,(path,digest) in pins.items():
        raw=(BASE/path).read_bytes();assert sha(raw)==digest;proofs[key]=json.loads(raw)
        assert proofs[key]['source']==SOURCE and proofs[key]['actualExit']==0
    old=proofs['prior']['sourceRows'];hashes=proofs['normal']['begin']['inputHashes'];assert len(old)==626
    assert proofs['post']['confirmedCandidates']==47 and proofs['post']['literalOwnerTable']==ORACLE
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes());logical={row['path']:row for row in inventory['artifacts']}
    original=[dict(path=row['path'],sha256=row['sha256'],owner=row['legacyReportedOwner']) for row in old]
    known={row['path'] for row in old}
    for path,item in sorted(resolver.DECISIONS.items()):
        assert path not in known and path not in logical and item['owner']==item['costOwner']==ORACLE[short(path)]
        assert sha((ROOT/path).read_bytes())==hashes[path]==item['sha256']
        original.append(dict(path=path,sha256=hashes[path],owner=None))
    rows=resolver.join_rows(original,logical,hashes,'WBS-G13.07');resolver.validate(rows,original,logical,hashes,'WBS-G13.07')
    assert len(rows)==len({row['path'] for row in rows})==673
    for before,after in zip(old,rows):assert all(before[k]==after[k] for k in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
    for row in rows[626:]:assert row['canonicalOwner']==row['canonicalCostOwner']==ORACLE[short(row['path'])]
    rejected=[]
    for label,change in (('cost-only',lambda v:v[626].update(canonicalCostOwner='WBS-G13.07')),
      ('owner-only',lambda v:v[626].update(canonicalOwner='WBS-G13.07')),('accepted-invented',lambda v:v[626].update(ownershipStatus='ACCEPTED')),
      ('missing',lambda v:v.pop()),('duplicate',lambda v:v.append(copy.deepcopy(v[0]))),('wrong-hash',lambda v:v[626].update(sha256='0'*64))):
        changed=copy.deepcopy(rows);change(changed)
        if label=='cost-only':assert {k for k in rows[626] if rows[626][k]!=changed[626][k]}=={'canonicalCostOwner'}
        try:resolver.validate(changed,original,logical,hashes,'WBS-G13.07')
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged mapping accepted')
    for path in resolver.DECISIONS:
        neighbor=path.removesuffix('.java')+'Foreign.java'
        assert resolver.canonical(neighbor,logical)==resolver.previous.canonical(neighbor,logical)
    sample=next(iter(resolver.DECISIONS));fixture={**logical,sample:dict(path=sample,owner='WBS-F02',costOwner='WBS-F02')}
    assert resolver.canonical(sample,fixture)['canonicalOwner']=='WBS-F02'
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,inputs=pins,
          sourceRows=rows,sourceCount=673,newSourceOwnerCandidates=47,previous626CanonicalPreserved=True,
          independentLiteralTableVerified=True,positiveBeforeNegatives=True,metadataCounterexamples=rejected,neighbourInvariance=47,
          javaPaths=1789,registered=1498,registeredMain=965,totalMain=965,registeredTest=533,totalTest=824,unregisteredTest=291,
          productTestsExecuted=0,newTestIds=0,newMain=0,newAccepted=0,coverage=None,formalUpdated=False,wholeG13Accepted=False,
          whole451Accepted=False,wholeWbsAudit='HOLD_CURRENT_SOURCE_NOT_WHOLE_QUALIFIED',effortPercent=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,registered=1498,unregistered=291,metadataNegatives=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
