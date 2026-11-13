"""Price pure original snapshot7 worker and explicit observed-value oracle before changes."""
from pathlib import Path
import json,hashlib,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';i=b/'input';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
def wr(p,v):
 assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
old=next(d.glob('1641_*'));f=ld(old);est=dict(low=.35,base=1.05,high=2.1)
for k,v in est.items():
 for fld in ['additionalRequiredWorkGrossPp','additionalDiscoveredRemainingPp','revisedRemainingPp']:f[fld][k]=round(f[fld][k]+v,3)
f.update(previousForecast=ref(old),revision='420-MAINTENANCE_STOP_SNAPSHOT_PURE7_NORMAL_PLANNED',atJST=datetime.datetime.now().astimezone().isoformat(),latestAdditionalFinding=dict(workId='F03_BUG2866_STOP_SNAPSHOT_PURE_ORIGINAL7_NORMAL',estimate=est,capPp=3,sourceWorkerAndOracleSupplement=dict(low=.15,base=.45,high=.9),normalQualification=dict(low=.2,base=.6,high=1.2),reason='FiniteworkerBUG2866 plus genuine observedValues fixed12-order/immutable-list oracle absent from original7. Samewhole7 no Testextraction/authority substitution/oldsuccess confirmation, original cost unchanged.'))
br=f['currentFullForecastBudgetBridge'];br.update(asOfRevision=f['revision'],remainingCanonicalOriginalPricePp=f['remainingOriginalPlanPricePp'],additionalRemainingPp=f['additionalDiscoveredRemainingPp'],currentRevisedRemainingPp=f['revisedRemainingPp'])
for k in est:assert round(br['remainingCanonicalOriginalPricePp'][k]+br['additionalRemainingPp'][k]+br['historicalPartialAdjustmentPp'][k],3)==f['revisedRemainingPp'][k]
fp=d/'1643_WBS65予実・停止snapshot純七通常追加版420.json';wr(fp,f)
spec=b/'4267_停止snapshot原七・独立十二値と有限worker通常PT仕様.md';assert not spec.exists();spec.write_text('''# MaintenanceStopSnapshot whole原7・独立12値と有限worker

NK-OPS-001、P01804、OPS009/UI251253/SS341SSC100126/343354。BUG2866/YKT2387をPG30106へ修正前起票。追加資格 .35/1.05/2.1、上限3pp、原費用/元S/V不変更。

MSTOP001: Test手書きCOLD12行と固定8完全名/順序、cold・failedFailed・固定cg、回転入力同値。返却observedValuesを独立literal12要素（Id/loaded/inactive/dead/空/0/0/system.slice/no/空/空/0）の固定順でassertし返却List書換拒否を追加する。productionのPROPERTIES/encoderからexpectedを生成しない。
002: 全key欠落/重複/未知/区切り不正と終端LFを拒否、原input各byte保持。
003: 全byte位置のcontrol/nonASCII、2048/2049境界/nullとborrowedbyte消去後snapshot保持。
004: 固定配置・状態/numeric域、Job/PID非zeroとnonterminalのquiescent false。quiescentは停止/cleanjournal/Root権限ではない。
005: Invocation正準lower非zero32、timestamp非負u64/上限とoverflow/非正準拒否。
006: unit・timestamp・Invocation・PID各差分のmatches false、null拒否、同値true。
007: 8worker/64独立byteタスクで固定redaction/matches/quiescent、各Future5秒/finallyshutdownNow-await10assert。割込flagをpureparseで消費しない。元全golden/全assertを保持。

Main Snapshot/MaintenanceUnit/StopGateException/StopGateFailure全4physicalと原Test全7。JDK/JSpecify/JUnitだけ、native/Root/Unit/サービス/DB/VM/鍵/permit/FS操作0。sourcebody全4と全Testを先行読取り済み、HOLD試験の抽出や値から権限を作る代替0。GJF→RootNullAway/lintWerror→PMD/CS/SB→個別適用性→preflight→Git固定→whole7一回→別postの全CRC/初期化/単一exec/XML/四counterを確認。未達/失敗は原結果を保持し除外/期待値弱化なし。実行時刻/環境/command/source/終了/input/output/hashは各manifest、結果文書へ一意結合。実JVMCode対JaCoCo既定filter差は分離し、全451/generated-code例外承認・親stop成功・元190正式受入へ転用しない。
''')
mainbase='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/';names=['MaintenanceStopSnapshot','MaintenanceUnit','StopGateException','StopGateFailure'];mains=[mainbase+x+'.java' for x in names];inv=ld(r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json');owners={x['path']:x['owner'] for x in inv['artifacts']};c=ld(i/'2442_startup_proof8_profile.json');classes=['dev/codex/schubert/nk/batch/platform/'+x for x in names];before=b/'evidence/PG30106-p01804-whole-candidates-and-worker-before-fix-v1/manifest.json'
c.update(id='PG30122-STOP-SNAPSHOT-PURE7',productOwnerByMainPath={x:owners[x] for x in mains},oracleSpecs=[ref(spec)],closureProofs=[ref(before)],mainSources=mains,testSources=[dict(path=mainbase.replace('/main/','/test/')+'MaintenanceStopSnapshotTest.java',tests=7)],expectedTests=7,physicalClasses=[x+'.class' for x in classes],targetClasses=classes,pomInputs=['pom.xml','src/schubert-nk-batch/pom.xml'],slots={k:str((b/f'evidence/PG{v}-stop-snapshot7-{k}-v1').relative_to(r)) for k,v in dict(prestyle=30114,prepare=30116,static=30118,preflight=30120,unit=30122,post=30124).items()},privateDirs=dict(prepare='pg30116-stop-snapshot7-prepare-v1',unit='pg30122-stop-snapshot7-unit-v1'),newTestDefinitions=0);wr(i/'2450_stop_snapshot7_profile.json',c)
s=ld(i/'2443_startup_proof8_start.json');s.update(groupId='PGPT-WBS65-STOP-SNAPSHOT-PURE-ORIGINAL7-FINITE-WORKER-NORMAL-20261114',recordPath=str((d/'1644_WBS65停止snapshot原七通常開始.json').relative_to(r)),scope='BUG2866 whole pureJDKvalue MaintenanceStopSnapshotTest7 finiteworker64 plus genuine observedValues12literalorder/immutablelist oracle supplement. FourwholeMain physical4/fullstatic/fixedsource/onewhole7/independentpost. NoactualRootUnitDBVMnativeFSkeypermitservice actions/heldTestextraction/oldsuccessconfirmation.',oracleRefs=[ref(spec),ref(before)],run=c['id'],estimate=est,capPp=3,workIds=['F03_BUG2866_STOP_SNAPSHOT_PURE_ORIGINAL7_NORMAL'],forecastRef=ref(fp),nextCommand='Finite64workerandadd12literalobservedValuesimmutableoracle, allold7asserts unchanged. Fullstatic/oneGitfixedwhole7/independent4CRC-init-counters, preserveallmisses, noactualUnitoperations. Continue otherpermittedPGPT afterordinaryunit/report.');wr(i/'2451_stop_snapshot7_start.json',s)
print(json.dumps(dict(actualExit=0,estimate=est,remaining=f['revisedRemainingPp'])))
