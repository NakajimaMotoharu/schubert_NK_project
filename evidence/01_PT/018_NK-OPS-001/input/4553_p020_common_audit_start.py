"""Reserve the issued CLI scope audit, retaining original prices and all safety holds."""
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
row=next(x for x in csv.DictReader(plan.open(encoding='utf-8-sig'),delimiter='\t') if x['ID']=='WBS-P020-01.01/2-a')
estimate={k:float(row[v]) for k,v in [('low','楽観pp'),('base','残pp'),('high','慎重pp')]};assert estimate==dict(low=.166,base=.488,high=.976)
group='PGPT-WBS66-P020-COMMON-AUDIT-20261117';q=json.loads(Path(sys.argv[1]).read_text())
spec=b/'4464_P020共通CLI全体照合仕様.md';scope=spec.read_text()
values=dict(build_context(group_id=group,category='CONTRACT_AUDIT',kind='ORIGINAL_PLAN',scope=scope,
    oracle_refs=[ref(spec),ref(r/'documents/400_PGPT/470_PMO/484_WBSコスト枠・細分化.json')]),
    source='01c3b1a34ee01f4a43fcfd1eaa4cc945010675c9',headAtStart=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    wbsLeafIds=['WBS-P020-01.01','WBS-P020-01.02','WBS-P020-01.03'],managementWorkIds=[row['ID']],
    estimateAtGroupStartPp=estimate,groupCapPp=2,originalRow=row,additionalPricePp=0,
    newAcceptance=0,completedOriginalRowPricePp=0,nextCommand='Audit all five common Main, whole Test/helper/references and precise old proof applicability; bind required missing whole PT to three original child roles, then proceed existing /2-b without PMO wait. No actual Current/browser/native/DB/Root/VM/key operations.')
event=append_start(group,values,sys.argv[1],digest(q),datetime.datetime.now(datetime.timezone.utc).isoformat())
target=d/'050_P020共通CLI全体照合群開始.json';assert not target.exists();target.open('x').write(json.dumps(dict(actualExit=0,eventId=event,groupId=group,values=values,quota=q),ensure_ascii=False,indent=2)+'\n')
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
    p=r.parent/'PMO/pgpt-completion-stage-20261102'/name;v=json.loads(p.read_text());v.update(lastEventId=event,ordinaryActiveGroup=group,ordinaryGroupNotYetClosed=True,currentQuota=q,latestWbs66Record=ref(target),mayFinishTurn=False,executionAllowed=True,newImplementationAllowed=True,nextCommand=values['nextCommand']);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,event=event,estimate=estimate,cap=2,existingRow=row['ID'])))
