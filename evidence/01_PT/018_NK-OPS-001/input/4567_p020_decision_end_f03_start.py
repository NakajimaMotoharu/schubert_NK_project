"""Return unresolved original criteria and continue permitted original F03 source review."""
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
b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
s=load(d/'055_P020個別判定群開始.json');pp=b/'evidence/PG37030-p020-original-criteria-decision-v1/manifest.json';p=load(pp);assert p['actualExit']==0 and p['acceptance']=='NOT_ACCEPTED'
q=load(Path(sys.argv[1]));now=datetime.datetime.now(datetime.timezone.utc).isoformat();bound=end_fields(s['quota'],q,digest(q),now,p['terminalAtUTC'],1)
assert not any(x['groupId']==s['groupId'] and x.get('groupBoundary')=='END' for x in map(json.loads,metrics.EVENTS.read_text().splitlines()))
v=dict(bound,source=p['sourceCore'],actualUnitSource=p['actualUnitSource'],groupBoundary='END',wbsLeafIds=s['values']['wbsLeafIds'],workCategory='CONTRACT_AUDIT',workAttributionKind='ORIGINAL_PLAN',managementWorkIds=['WBS-P020-01.01/2-c'],estimateAtGroupStartPp=s['values']['estimateAtGroupStartPp'],groupCapPp=1,completedOriginalRowPricePp=.25,addedPricePp=0,newAcceptance=0,formalUpdated=False,effortCompletionRate=None,proof=ref(pp),criterionReductions=['Original three children and nine checks assessed individually, F02 unresolved explicitly prevents acceptance; source/quality/trace missing facts returned','No formal/effort progress inferred from completed documentation price or Test count'],remainingDetailBasePp='1092.098')
event=metrics.append(s['groupId'],'CHECKPOINT',v);target=d/'057_P020個別判定返却・原残.json';target.open('x').write(json.dumps(dict(actualExit=0,eventId=event,values=v,quota=q),ensure_ascii=False,indent=2)+'\n')
plan=r.parent/'PMO/hourly-monitor/wbs66-20261116/58_直近20pp不足時の対象と予算判断を実行用の検収表へ渡す/WBS.tsv';row=next(x for x in csv.DictReader(plan.open(encoding='utf-8-sig'),delimiter='\t') if x['ID']=='WBS-F03/2-2');estimate={k:float(row[x]) for k,x in [('low','楽観pp'),('base','残pp'),('high','慎重pp')]};assert estimate==dict(low=.9,base=2.4,high=4.8)
group='PGPT-WBS66-F03-PMD-APPLICABILITY-20261117';spec=b/'4468_F03静的適用性分類仕様.md'
spec.open('x').write('# F03 既存原PMD指摘の適用性分類\n\n原F03/2-2開始.9/2.4/4.8pp、cap6、未完行の元価格2.4を維持し新規費用を増額しない。Core01cのPG36960/36968にある全Bootstrap87/Batch200の原971siteを使用。原XML/source一致の既分類候補309と未分類662を最終分類と混同しない。旧成功PT/SB/compileは確認再演しない。\n\n各siteのpath/hash/line/column/rule/所属class-method・規約/原SS/owner・元Test又は静的適用根拠を保持する。まずDoNotUseThreads等について、PMD7.28原rule本文とstandalone六module/JDK25構成を照合し、JavaEE container前提と原siteが該当するかを全件判断する。一般的なthread-safe説明だけで全ルールを一括非該当としない。実挙動の適否が必要な指摘は未分類を維持、障害を認定すれば修正前に起票する。\n\nsource/POM/rule/Suppression変更0、反射/4保留型classfile/Root11/native/DB/VM/service/鍵操作0。分類だけで機能PT/並行/native/coverage完了に代替しない。元owner/cost/SS変更は不要、必要な設計不備はSSC等を先行する。終了時に全971の集合一致、分類済/未分類/要是正件数と具体次証拠を返す。全F03/451/190受入は別判定。\n')
values=dict(build_context(group_id=group,category='STATIC_ANALYSIS',kind='ORIGINAL_PLAN',scope=spec.read_text(),oracle_refs=[ref(spec),ref(r/'tools/quality/static/pmd.xml')]),source=p['sourceCore'],actualUnitSource=p['actualUnitSource'],wbsLeafIds=['WBS-F03'],managementWorkIds=[row['ID']],estimateAtGroupStartPp=estimate,groupCapPp=6,originalRow=row,additionalPricePp=0,newAcceptance=0,completedOriginalRowPricePp=0,nextCommand='Read PMD7.28 rule source and exact current unmatched site closures, beginning169 DoNotUseThreads/J2EE applicability; bind each site to standalone module/build/SS owner without hiding functional/native/QA056 holds. Retain all971 raw XML and no confirmation test replay.')
event2=append_start(group,values,sys.argv[1],digest(q),datetime.datetime.now(datetime.timezone.utc).isoformat());target2=d/'058_F03原PMD適用性群開始.json';target2.open('x').write(json.dumps(dict(actualExit=0,eventId=event2,groupId=group,values=values,quota=q),ensure_ascii=False,indent=2)+'\n')
summary='P020当124/別5真正成功と独立post0、原三子9criteriaへ返却。14生成methodを新五件で有意に検証したがraw/compiler/private ctor/trace及びF02依存が残り親受入0、17/190/1964-53/工数null維持。元a .488/b1.5/c.25の予定成果（未解決条件の明示を含む）だけ完了、元既存累計7.288pp・追加3.150pp・残1092.098pp、実費/完成率でない。現在は元F03/2-2 .9/2.4/4.8 cap6で原971site/未分類662の適用性reviewへ継続。'
for name in ['456_領域別進捗・利用枠・中断再開管理.md','460_基盤残件・再開優先順.md']:
 f=r/'documents/400_PGPT/450_品質'/name;title,body=f.read_text().split('\n',1);f.write_text(title+'\n\n## WBS66 P020個別判定返却・F03継続 '+now+'\n\n'+summary+' own unit/static/post全真正terminal0、haruka scratch保持・他操作0、fresh残'+str(q['primary']['remainingPercent'])+'。次 '+values['nextCommand']+'\n'+body)
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
 f=r.parent/'PMO/pgpt-completion-stage-20261102'/name;x=load(f);x.update(lastEventId=event2,currentQuota=q,ordinaryActiveGroup=group,ordinaryGroupNotYetClosed=True,latestWbs66Record=ref(target2),remainingDetailBasePp='1092.098',mayFinishTurn=False,executionAllowed=True,newImplementationAllowed=True,nextCommand=values['nextCommand']);f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,endEvent=event,startEvent=event2,completedPricePp=.25,remaining='1092.098',newAcceptance=0)))
