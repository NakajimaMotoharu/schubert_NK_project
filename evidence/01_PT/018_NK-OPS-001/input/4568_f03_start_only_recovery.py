"""Retain genuine prior END, validate actual schema, append only missing original F03 START."""
from pathlib import Path
import copy
import csv
import datetime
import hashlib
import json
import sys

r=Path.cwd();sys.path[:0]=[str(r/'tools/quality'),str(r/'tools/quality/vm/050_s1')]
import pg998_metrics as metrics
from pmo_quota_binding import append_start,digest
from pmo_group_context import build_context,validate_context
b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
saved=load(d/'057_P020個別判定返却・原残.json');assert saved['eventId']=='PGPT-20261008-5604' and saved['values']['completedOriginalRowPricePp']==.25
rows=list(map(json.loads,metrics.EVENTS.read_text().splitlines()));assert sum(x['eventId']==saved['eventId'] for x in rows)==1
p=load(b/'evidence/PG37030-p020-original-criteria-decision-v1/manifest.json');spec=b/'4468_F03静的適用性分類仕様.md';group='PGPT-WBS66-F03-PMD-APPLICABILITY-20261117'
assert not any(x['groupId']==group and x.get('eventType')=='GROUP_START' for x in rows)
refs=[ref(spec),ref(b/'evidence/PG36968-current287-pmd971-candidates-v2/manifest.json')]
kwargs=dict(group_id=group,category='CONTRACT_AUDIT',kind='ORIGINAL_PLAN',scope=spec.read_text(),oracle_refs=refs);context=build_context(**kwargs);validate_context(group,context)
for field,value in [('category','STATIC_ANALYSIS'),('oracle_refs',[dict(path='tools/quality/static/pmd.xml',sha256=sha(r/'tools/quality/static/pmd.xml'))]),('oracle_refs',[dict(path='evidence/01_PT/018_NK-OPS-001/test.xml',sha256='0'*64)])]:
 bad=copy.deepcopy(kwargs);bad[field]=value
 try:build_context(**bad)
 except ValueError:pass
 else:raise AssertionError('invalid context accepted')
plan=r.parent/'PMO/hourly-monitor/wbs66-20261116/58_直近20pp不足時の対象と予算判断を実行用の検収表へ渡す/WBS.tsv';row=next(x for x in csv.DictReader(plan.open(encoding='utf-8-sig'),delimiter='\t') if x['ID']=='WBS-F03/2-2');estimate={k:float(row[x]) for k,x in [('low','楽観pp'),('base','残pp'),('high','慎重pp')]};assert estimate==dict(low=.9,base=2.4,high=4.8)
q=load(Path(sys.argv[1]));now=datetime.datetime.now(datetime.timezone.utc).isoformat();values=dict(context,source=p['sourceCore'],actualUnitSource=p['actualUnitSource'],wbsLeafIds=['WBS-F03'],managementWorkIds=[row['ID']],estimateAtGroupStartPp=estimate,groupCapPp=6,originalRow=row,additionalPricePp=0,newAcceptance=0,completedOriginalRowPricePp=0,originalPmdRule=dict(path='tools/quality/static/pmd.xml',sha256=sha(r/'tools/quality/static/pmd.xml')),schemaNegativeChecks=3,priorEndReplayed=False,nextCommand='Read pinned PMD7.28 rule source and current unmatched site closures. Classify original169 DoNotUseThreads by J2EE-container applicability and standalone module/SS owner, retaining all functional/native/QA056 holds. No repeated successful Main477/124/SB/PT.')
event=append_start(group,values,sys.argv[1],digest(q),now);target=d/'058_F03原PMD適用性群開始.json';target.open('x').write(json.dumps(dict(actualExit=0,eventId=event,groupId=group,values=values,quota=q),ensure_ascii=False,indent=2)+'\n')
summary='P020原三子9criteriaへ当124成功/別5成功/静的全五の証拠を返却、F02依存/未網羅/trace未成立で新規元190受入0。原a/b/c完了価格2.238、元既存累計7.288・追加3.150・残1092.098pp、工数null/正式1964-53不変。群切替4567はmetadata schema誤りで終了1、既END5604は保存し再発行0、新STARTだけ正schema/負3で復旧。F03 original2.4行は未完のまま、原971site/未分類662の適用性reviewへ継続。'
for name in ['456_領域別進捗・利用枠・中断再開管理.md','460_基盤残件・再開優先順.md']:
 f=r/'documents/400_PGPT/450_品質'/name;title,body=f.read_text().split('\n',1);f.write_text(title+'\n\n## WBS66 P020判定返却・F03分類開始 '+now+'\n\n'+summary+' own job全terminal0・haruka scratch保持/実サービス等操作0、fresh残'+str(q['primary']['remainingPercent'])+'、event '+event+'。次 '+values['nextCommand']+'\n'+body)
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
 f=r.parent/'PMO/pgpt-completion-stage-20261102'/name;x=load(f);x.update(lastEventId=event,currentQuota=q,ordinaryActiveGroup=group,ordinaryGroupNotYetClosed=True,latestWbs66Record=ref(target),remainingDetailBasePp='1092.098',mayFinishTurn=False,executionAllowed=True,newImplementationAllowed=True,nextCommand=values['nextCommand']);f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,event=event,negativeChecks=3,priorEndReplayed=False,estimate=estimate,newAcceptance=0)))
