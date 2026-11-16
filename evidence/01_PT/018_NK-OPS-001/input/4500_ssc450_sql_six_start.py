"""Price the necessary SQL6 corrective PG/PT once, preserving canonical owner and original budget."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

r=Path.cwd();sys.path[:0]=[str(r/'tools/quality'),str(r/'tools/quality/vm/050_s1')]
from pmo_group_context import build_context
from pmo_quota_binding import append_start,digest
b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117'
s=r.parent/'PMO/pgpt-completion-stage-20261102'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
q=json.loads(Path(sys.argv[1]).read_text());group='PGPT-WBS66-SSC450-LITERAL-SQL6-20261117'
core='e8822b0e40d08a0a733bd21b6866b3ece3de5b65'
scope=('Additional necessary A corrective PG/PT for BUG3132/YKT2603, all six migration SQL Main '
 'canonical owner/cost P01903; F03 receives the result but original costs are not reassigned. '
 'Private constant SQL-operation callbacks, same SQL bytes/order/borrowed TX/resource/null/API, '
 'no new suppression or exclusions. Whole independent160 tests plus genuinely required whole '
 'helpers, exact source/byte/raw/static and post. No real DB/master/key/Root/VM/native/fourheld '
 'operations. Existing ordinary memory-only tests are the default; preserve unknown/HOLD scopes.')
values=dict(build_context(group_id=group,category='IMPLEMENTATION',kind='ADDITIONAL_FINDING',
    scope=scope,oracle_refs=[ref(b/'4453_SSC450閉SQL六Main単体仕様.md'),
                           ref(b/'evidence/PG36854-ssc449-four-main-partial-return-v2/manifest.json')]),
    source=core,headAtStart=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    wbsLeafIds=['WBS-P019-03.01','WBS-P019-03.02','WBS-P019-03.03'],
    managementWorkIds=['追加A-SSC450-SQL6'],managementPlan='WBS66-58-20261117-SHORTTERM',
    estimateAtGroupStartPp=dict(low=.4,base=1.2,high=3.6),groupCapPp=4,
    canonicalChangeAndCostOwner='WBS-P019-03',resultRecipient='WBS-F03',
    sameSharedWorkChargedOnce=True,originalF03CRowRemainingPp=2.4,
    completedOriginalRowPricePp=0,additionalStartedPricePp=1.2,
    remainingDetailWithAddedUnfinishedPp='1095.536',
    newAcceptance=0,actualAllocatedPp=None,tokenTotals=None,
    nextCommand='Register/publish SSC450 internal detail, then manufacture six SQL Main; preserve original160 tests and prove exact SQL equivalence before frozen-source ordinary unit/static/raw.')
event=append_start(group,values,sys.argv[1],digest(q),datetime.datetime.now(datetime.timezone.utc).isoformat())
p=d/'039_SSC450閉SQL六Main群開始.json';p.open('x').write(json.dumps(dict(actualExit=0,
    eventId=event,groupId=group,values=values,quota=q),ensure_ascii=False,indent=2)+'\n')
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
    path=s/name;v=json.loads(path.read_text());v.update(lastEventId=event,
       ordinaryActiveGroup=group,ordinaryGroupNotYetClosed=True,currentQuota=q,
       currentWbs66RemainingDetailBasePp='1095.536',mayFinishTurn=False,
       executionAllowed=True,newImplementationAllowed=True,latestWbs66Record=ref(p),
       nextCommand=values['nextCommand']);path.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,event=event,additionalBasePp=1.2,cap=4,
    canonicalCostOwner='WBS-P019-03',newOriginal190Acceptance=0)))
