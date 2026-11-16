"""Close original scope audit and reserve original whole CLI PT, without synthetic acceptance."""
from pathlib import Path
import csv
import datetime
import hashlib
import json
import sys

r=Path.cwd();sys.path[:0]=[str(r/'tools/quality'),str(r/'tools/quality/vm/050_s1')]
import pg998_metrics as metrics
from pmo_quota_binding import append_start,digest,end_fields
from pmo_group_context import build_context
b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
s=load(d/'050_P020共通CLI全体照合群開始.json');pp=b/'evidence/PG37004-p020-whole-scope-audit-v1/manifest.json';p=load(pp)
q=load(Path(sys.argv[1]));now=datetime.datetime.now(datetime.timezone.utc).isoformat();bound=end_fields(s['quota'],q,digest(q),now,p['terminalAtUTC'],2)
assert not any(x['groupId']==s['groupId'] and x.get('groupBoundary')=='END' for x in map(json.loads,metrics.EVENTS.read_text().splitlines()))
v=dict(bound,source=p['sourceCore'],actualUnitSource=p['actualUnitSource'],groupBoundary='END',wbsLeafIds=s['values']['wbsLeafIds'],workCategory='CONTRACT_AUDIT',workAttributionKind='ORIGINAL_PLAN',managementWorkIds=['WBS-P020-01.01/2-a'],estimateAtGroupStartPp=s['values']['estimateAtGroupStartPp'],groupCapPp=2,completedOriginalRowPricePp=.488,addedPricePp=0,newAcceptance=0,formalUpdated=False,effortCompletionRate=None,proof=ref(pp),criterionReductions=['Five Main and seventeenth whole suite/124 invocations now bound to original three child roles','Old10/60 changes and helper closure determined; current tests required, no source-success transfer','C02 duplicate confirmation avoided; effective Unit/owner condition remains held'],remainingDetailBasePp='1093.848')
event=metrics.append(s['groupId'],'CHECKPOINT',v);target=d/'051_P020全体照合終了.json';target.open('x').write(json.dumps(dict(actualExit=0,eventId=event,values=v,quota=q),ensure_ascii=False,indent=2)+'\n')
plan=r.parent/'PMO/hourly-monitor/wbs66-20261116/58_直近20pp不足時の対象と予算判断を実行用の検収表へ渡す/WBS.tsv'
row=next(x for x in csv.DictReader(plan.open(encoding='utf-8-sig'),delimiter='\t') if x['ID']=='WBS-P020-01.01/2-b')
estimate={k:float(row[x]) for k,x in [('low','楽観pp'),('base','残pp'),('high','慎重pp')]};assert estimate==dict(low=.511,base=1.5,high=2.999)
group='PGPT-WBS66-P020-COMMON-WHOLE124-20261117';spec=b/'4465_P020全体照合結果・通常124仕様.md'
values=dict(build_context(group_id=group,category='SELECTED_TEST',kind='ORIGINAL_PLAN',scope=spec.read_text(),oracle_refs=[ref(spec),ref(pp)]),source=p['sourceCore'],actualUnitSource=p['actualUnitSource'],wbsLeafIds=s['values']['wbsLeafIds'],managementWorkIds=[row['ID']],estimateAtGroupStartPp=estimate,groupCapPp=4,originalRow=row,additionalPricePp=0,newAcceptance=0,completedOriginalRowPricePp=0,nextCommand='Freeze public snapshot and SDK plus bounded ordinary javac/JUnit124 runner, authenticate fresh owned haruka scratch, launch exactly once. Keep real Current/NK/native/Root/service/DB and pending QA056 operations held. Independently recover genuine terminal/XML/CRC/raw without replay.')
# Separate actual receipt binding per group; this receipt has not been used for a start.
event2=append_start(group,values,sys.argv[1],digest(q),datetime.datetime.now(datetime.timezone.utc).isoformat())
target2=d/'052_P020通常124群開始.json';target2.open('x').write(json.dumps(dict(actualExit=0,eventId=event2,groupId=group,values=values,quota=q),ensure_ascii=False,indent=2)+'\n')
summary='P020共通五Main/全Test閉包照合を完了。旧10はMain/Test変更、旧60は三Test及び依存helper変更のため新source全17suite124を必要PTへ確定。旧成功の転用/再演0。元a .488だけ完了、既存累計5.538pp、追加3.150pp不変、残1093.848ppは価格で工数率でない。現在は元b1.5pp cap4で当124の実施準備、未実行124、正式1964/53・元190新規0・工数null。harukaはmini/known-host/工具/空き読取認証済、実サービス/DB/VM操作0。C02は同source原証拠再演不要、実効Unit/native/ownerは保留。'
for name in ['456_領域別進捗・利用枠・中断再開管理.md','460_基盤残件・再開優先順.md']:
 f=r/'documents/400_PGPT/450_品質'/name;title,body=f.read_text().split('\n',1);f.write_text(title+'\n\n## WBS66 P020全体照合・通常124着手 '+now+'\n\n'+summary+' 次 '+values['nextCommand']+'\n'+body)
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
 f=r.parent/'PMO/pgpt-completion-stage-20261102'/name;v=load(f);v.update(lastEventId=event2,ordinaryActiveGroup=group,ordinaryGroupNotYetClosed=True,currentQuota=q,latestWbs66Record=ref(target2),remainingDetailBasePp='1093.848',mayFinishTurn=False,executionAllowed=True,newImplementationAllowed=True,nextCommand=values['nextCommand']);f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,endEvent=event,startEvent=event2,existingCompletedPricePp=.488,remaining='1093.848',unitExpected=124,newAcceptance=0)))
