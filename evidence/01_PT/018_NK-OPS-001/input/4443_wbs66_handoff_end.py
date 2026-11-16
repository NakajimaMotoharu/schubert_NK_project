"""Independently verify current foundation packets and record completed plan rows once."""
from pathlib import Path
from decimal import Decimal
import datetime,hashlib,json,sys
r=Path.cwd();sys.path[:0]=[str(r/'tools/quality'),str(r/'tools/quality/vm/050_s1')]
import pg998_metrics as metrics
from pmo_quota_binding import digest,end_fields
b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117';s=r.parent/'PMO/pgpt-completion-stage-20261102'
ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));wr=lambda p,v:p.open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
a=ld(d/'007_基盤四担当引渡し群開始.json');e=b/'evidence/PG36650-wbs66-foundation-four-handoff-v1';m=ld(e/'manifest.json');assert m['actualExit']==0 and m['newAcceptance']==0 and m['formalUpdated'] is False
for item in m['evidenceFiles']+[x['document'] for x in m['handoffs']]:assert sha(r/item['path'])==item['sha256']
modules=ld(e/'current-six-module-source-inventory.json')['modules'];assert len(modules)==6 and sum(x['mainSourceCount'] for x in modules)==1022
for module in modules:
 for pin in module['sourcePins']:assert sha(r/pin['path'])==pin['sha256']
assert len(ld(e/'f02-thirteen-requirements.json')['requirements'])==13
configs=ld(e/'c02-fourteen-configs.json')['configs'];assert len(configs)==14 and all(sha(r/x['path'])==x['sha256'] and x['matchesPriorSourceBytes'] for x in configs)
assert len(m['handoffs'])==4 and all(len(x['criterionIds'])==4 and x['parentAccepted'] is False for x in m['handoffs'])
terminal=datetime.datetime.now(datetime.timezone.utc).isoformat()
if len(sys.argv)==1:
 wr(e/'independent-post.json',dict(actualExit=0,atUTC=terminal,source=m['source'],manifest=ref(e/'manifest.json'),modules=6,mainSource1022Exact=True,requirements=13,configs=14,roleHandoffs=4,criterionIds=16,productTestsExecuted=0,newAcceptance=0,formalUpdated=False));print('independent post 0');raise SystemExit(0)
post=ld(e/'independent-post.json');assert post['actualExit']==0
q=ld(Path(sys.argv[1]));first=next(x for x in map(json.loads,metrics.EVENTS.read_text().splitlines()) if x['eventType']=='GROUP_START' and x['groupId']==a['groupId']);assert not any(x.get('groupBoundary')=='END' and x['groupId']==a['groupId'] for x in map(json.loads,metrics.EVENTS.read_text().splitlines()))
bound=end_fields(a['quota'],q,digest(q),datetime.datetime.now(datetime.timezone.utc).isoformat(),post['atUTC'],7)
remaining=str(Decimal('1098.486')-Decimal('3.4'));assert remaining=='1095.086'
nextcmd='Continue WBS-F03/2-2 permitted six-module static source/tool applicability; retain Root11 and specifically held operations. Prepare P004-03/P004-05 independent contract/TestID matrices and reuse original source-matched proofs. Resolve concrete missing permission only if indispensable, never replay refused operations.'
forecast=dict(originalWbs66DetailPp='1099.386',priorCompletedSupplementPp='.900',thisCompletedExistingRowsPp='3.400',completedTaskPricePp='4.300',remainingDetailBasePp=remaining,scopeAcceptanceNetDelta=0,effortCompletionRate=None,observedSharedPp=bound['observedSharedPp'],actualAllocatedPp=None,tokenTotals=None,conditionalCapacityRecoveryPp='1.200',conditionalCapacityRecoveryStatus='NOT_PERFORMED_NOT_COMPLETED_NO_CLEANUP_REQUIRED_FOR_BOUNDED_WORK',oldWbs65ForecastFrozen=True,costReductionIsNotProgress=True)
wr(d/'013_四担当引渡し予実・残明細.json',forecast)
values=dict(bound,source=m['source'],run='PG36650-WBS66-FOUNDATION-FOUR-HANDOFF',wbsLeafIds=first['wbsLeafIds'],workCategory=first['workCategory'],workAttributionKind=first['workAttributionKind'],managementWorkIds=first['managementWorkIds'],estimateAtGroupStartPp=first['estimateAtGroupStartPp'],groupCapPp=7,groupBoundary='END',completedExistingRowPricePp=3.4,sourceEvidenceRefs=[ref(e/'manifest.json'),ref(e/'independent-post.json')],acceptedDelta=dict(closedIds=[],reopenedIds=[],criteriaSatisfied=[],evidenceRefs=[]),criterionReductions=['F02: six-module current-source inventory and 13 requirements gaps are named; remaining current six-module build/runtime evidence','F03: six-module current/historical applicability and held operations are explicit; only Protocol current static qualified','C02: fourteen source configs are unchanged with exact hashes; effective-unit/native-owner/current-source postconditions outstanding','F04: existing haruka setup/read-execute baseline supplied; actual source/ownership/end conditions outstanding'],newAcceptance=0,effortCompletionRate=None,nextCommand=nextcmd)
event=metrics.append(a['groupId'],'CHECKPOINT',values);result=dict(actualExit=0,eventId=event,groupId=a['groupId'],source=m['source'],quota=q,forecast=forecast,criteriaStillPending=m['criteriaStillPending'],sourceEvidenceRefs=values['sourceEvidenceRefs'],originalAcceptanceGross=0,originalAcceptanceNet=0,formalUpdated=False,nextCommand=nextcmd)
wr(d/'014_四担当引渡し群終了.json',result)
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
 p=s/name;v=ld(p);v.update(phase='WBS66_ACTIVE',lastEventId=event,ordinaryActiveGroup=None,ordinaryGroupNotYetClosed=False,currentQuota=q,executionAllowed=True,newImplementationAllowed=bound['newImplementationAllowedByQuota'],mayFinishTurn=False,pgptAllComplete=False,latestWbs66Record=ref(d/'014_四担当引渡し群終了.json'),currentWbs66RemainingDetailBasePp=remaining,currentWbs66Forecast=ref(d/'013_四担当引渡し予実・残明細.json'),nextCommand=nextcmd);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
for name in ['456_領域別進捗・利用枠・中断再開管理.md','460_基盤残件・再開優先順.md']:
 p=r/'documents/400_PGPT/450_品質'/name;old=p.read_text();header,body=old.split('\n',1);p.write_text(header+'\n\n## WBS66 四担当引渡し完了 '+now+'\n\nPG36650/source '+m['source']+'・独立post0。六module 1022Main、13SYS、14設定、四担当16判定IDの不足を資料008～012へ明示。正式受入増0、F02/F03/C02/F04未受入。SSC447 152PASSは限定。今回既存8行3.4pp、累計計画価格4.3pp、残明細1095.086pp（実費/工数率ではない）。共有差 '+str(bound['observedSharedPp'])+'pp、専有実費/token不明。event '+event+'。次: '+nextcmd+'\n\n'+body)
print(json.dumps(dict(actualExit=0,event=event,planPrice=3.4,remaining=remaining,newAcceptance=0,observedSharedPp=bound['observedSharedPp'])))
