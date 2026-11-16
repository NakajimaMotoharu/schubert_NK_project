"""Reserve the existing A2 row, with exact original pure-public-provider operation boundary."""
from pathlib import Path
import csv
import datetime
import hashlib
import json
import subprocess
import sys

r=Path.cwd();sys.path[:0]=[str(r/'tools/quality'),str(r/'tools/quality/vm/050_s1')]
from pmo_group_context import build_context
from pmo_quota_binding import append_start,digest
b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
plan=r.parent/'PMO/hourly-monitor/wbs66-20261116/58_直近20pp不足時の対象と予算判断を実行用の検収表へ渡す/WBS.tsv'
row=next(x for x in csv.DictReader(plan.open(encoding='utf-8-sig'),delimiter='\t') if x['ID']=='A2-28.01')
estimate={k:float(row[v]) for k,v in [('low','楽観pp'),('base','残pp'),('high','慎重pp')]};assert estimate==dict(low=1.5,base=3.9,high=7.7)
core='01c3b1a34ee01f4a43fcfd1eaa4cc945010675c9';spec=b/'4459_P01808現Checkpoint通常PT・fatal三境界仕様.md'
original=b/'evidence/provisional/PG17624-checkpoint-public-provider-twelve-independent-v1/manifest.json'
assert json.loads(original.read_text())['actualExit']==0
scope=('Existing A2-28.01: current whole Checkpoint public provider12 plus three independently specified fatal catalog cases. Original pure public-reflection/fake provider/memory export boundary is approved by saved PG17620/24; change since old Main is only three preserveFatal calls. No closed_host_profile DENIED or reflection guard is changed or probed. This uses ordinary original Test compilation/JUnit, not a retry of refused operations. All four QA056 held classes are absent from complete Bootstrap/Storage classpaths. Reserved native exporter/hash/file/root/StopHold owned TERM/DB/VM/key/intent/failed-cohort operations stay held. Reuse original14 only by exact Main/Test/byte proof; never merge old exec or grant parent acceptance. Specification4459 froze the plan price before the new Test file was written; GROUP_START recorded now, no earlier timestamp invented.')
group='PGPT-WBS66-P01808-CHECKPOINT-20261117';q=json.loads(Path(sys.argv[1]).read_text())
values=dict(build_context(group_id=group,category='SELECTED_TEST',kind='ORIGINAL_PLAN',scope=scope,oracle_refs=[ref(spec),ref(original)]),source=core,headAtStart=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),wbsLeafIds=['WBS-P018-08.01','WBS-P018-08.02','WBS-P018-08.03'],managementWorkIds=['A2-28.01'],estimateAtGroupStartPp=estimate,groupCapPp=8,canonicalArtifactOwner='WBS-P018-08',additionalPricePp=0,completedOriginalRowPricePp=0,newAcceptance=0,nextCommand='Prepare exact two whole Test source/current Root280 classpaths, ordinary format/CS/PMD/Test compile; qualify all static findings before freezing source and single15 normal JUnit; post/raw retain native gaps.')
event=append_start(group,values,sys.argv[1],digest(q),datetime.datetime.now(datetime.timezone.utc).isoformat())
target=d/'046_P01808現Checkpoint通常15群開始.json';target.open('x').write(json.dumps(dict(actualExit=0,eventId=event,groupId=group,values=values,quota=q),ensure_ascii=False,indent=2)+'\n')
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
    p=r.parent/'PMO/pgpt-completion-stage-20261102'/name;v=json.loads(p.read_text());v.update(lastEventId=event,ordinaryActiveGroup=group,ordinaryGroupNotYetClosed=True,currentQuota=q,productionCoreMain=core,latestWbs66Record=ref(target),mayFinishTurn=False,executionAllowed=True,newImplementationAllowed=True,nextCommand=values['nextCommand']);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,event=event,existingRow='A2-28.01',estimate=estimate,cap=8)))
