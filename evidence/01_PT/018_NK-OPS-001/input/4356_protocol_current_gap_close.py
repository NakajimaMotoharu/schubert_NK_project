"""Close only the current raw-gap partition; do not count review as production testing."""
from pathlib import Path
from decimal import Decimal
import datetime, hashlib, json
from pmo_forecast_bridge import reconcile_current_bridge
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106'
ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));wr=lambda p,v:p.open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
mp=b/'evidence/PG36300-current-protocol-raw-gap-partition-v1/manifest.json';m=ld(mp)
assert m['actualExit']==0 and m['missingMethodCount']==33 and len(m['sourceWitness'])==19 and m['applicationTestsExecuted']==0
prior=next(d.glob('2441*'));f=ld(prior)
f.update(revision='769-CURRENT_PROTOCOL_RAW_GAP_PARTITION_COMPLETE',previousForecast=ref(prior),atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat())
for k,v in dict(low=.06,base=.18,high=.54).items():
 for key,delta in [('additionalCompletedWorkPp',v),('additionalDiscoveredRemainingPp',-v),('revisedRemainingPp',-v)]:f[key][k]=float(Decimal(str(f[key][k]))+Decimal(str(delta)))
f['currentFullForecastBudgetBridge']=reconcile_current_bridge(f)
tech=dict(currentCoreSource=m['productionCoreMain'],originalUnitSource=m['actualUnitSource'],reusedOriginalWholeRun='PG36280',missingMethods=33,publicValueMissingMethods=27,publicValueClasses=10,unusedUtilityConstructors=6,missingBranches=59,branchMethods=17,compilerSwitchMapMisses=4,compilerMapMissingInstructions=16,currentSourceWitnesses=19,applicationTestsExecuted=0,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None)
f['latestGroupTechnicalResult']=tech;fp=d/'2443_WBS65予実・現source残条件分割完了版769.json';wr(fp,f)
summary='Core7f04/Unit5b12/PG36300 当source全145の元36284 rawをpin照合し、残33methodを十public値classの27method＋六utility ctorへ一意分割、59branchを17methodへ独立加算照合、別の四compiler map16instructionも保持。関係Main19は現byteとCore git byte完全一致、classfile読取/define・製品実行・全145確認再演0。次通常PTをwire metadata三class、payload model七class、SS先行utility六/branch17の依存へ分けた。FieldDefinitionのvalue APIだけでswitch branchを合格化せず、WireMessageは不変payload identityとrecord key契約を区別する。監査.06/.18/.54限定完了・残397.324/837.386/1643.415、原904.85/SV保持、App248/36273/36206/歴史不成功67増加0、正式1964/53・正本184/625・元17/190・工数null不変。BUG3111/YKT2583global OPEN・全Root2Actual4/VMDBnative鍵aru等HOLD維持。'
e=b/'evidence/PG36302-current-protocol-gap-partition-join-v1';e.mkdir()
v=dict(actualExit=0,source=m['productionCoreMain'],productionCoreMain=m['productionCoreMain'],actualUnitSource=m['actualUnitSource'],terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),summary=summary,technical=tech,rawAudit=ref(mp),formalUpdated=False)
wr(e/'manifest.json',v);c=ld(b/'input/4354_protocol_current_gap_start.json')
c.update(recordPath=str((d/'2444_WBS65現source残条件分割終了.json').relative_to(r)),sourceAfter=m['productionCoreMain'],manifestPath=str((e/'manifest.json').relative_to(r)),manifestSha256=sha(e/'manifest.json'),terminalAtUTC=v['terminalAtUTC'],forecastRef=ref(fp),outcome='CURRENT_SOURCE_33METHOD_59BRANCH_PARTITIONED_GLOBAL_OPEN',technical=tech,checkpointText=summary,nextCommand='Commit/push. Price ordinary wire metadata ExpectedRoute/TransportMetadata/LargeResultContent value contracts first, preserve constructor negatives and independent constant wire/model inputs. Then seven aggregate model records and SS-reviewed six utilities/17branches/fourcompiler maps. No current145 replay or oldexecunion. Freshquota<=10/unavailable: stopnewwork, preserve next concrete command and latest actual own process; foreignVM UNKNOWN no query. Next hourly14:14:51.')
wr(b/'input/4357_protocol_current_gap_end.json',c)
(b/'4430_現sourceProtocol残条件分割・証跡照合結果.md').open('x').write('# 現sourceProtocol残条件分割・証跡照合結果\n\n'+summary+'\n\n'+str(mp)+' SHA256 '+sha(mp)+'。\n')
print(json.dumps(dict(actualExit=0,applicationTests=0,missingMethods=33,remaining=f['revisedRemainingPp'])))
