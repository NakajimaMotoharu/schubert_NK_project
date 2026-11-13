"""Price whole original pure-value StartupProofFrame8 before worker correction."""
from pathlib import Path
import json,hashlib,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';i=b/'input'
ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
def wr(p,v):
 assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
old=next(d.glob('1634_*'));f=ld(old);est=dict(low=.3,base=.9,high=1.8)
for k,v in est.items():
 for fld in ['additionalRequiredWorkGrossPp','additionalDiscoveredRemainingPp','revisedRemainingPp']:f[fld][k]=round(f[fld][k]+v,3)
f.update(previousForecast=ref(old),revision='417-STARTUP_PROOF_PURE_ORIGINAL8_NORMAL_PLANNED',atJST=datetime.datetime.now().astimezone().isoformat(),latestAdditionalFinding=dict(workId='F03_BUG2865_STARTUP_PROOF_PURE_ORIGINAL8_NORMAL',estimate=est,capPp=3,sourceWorkerFix=dict(low=.1,base=.3,high=.6),normalQualification=dict(low=.2,base=.6,high=1.2),reason='BUG2865 finite original pure-value worker; full oneMain/threephysical normal static+whole8+independentpost; no old success confirmation, heldTest extraction, actual authority or original cost reassignment.'))
br=f['currentFullForecastBudgetBridge'];br.update(asOfRevision=f['revision'],remainingCanonicalOriginalPricePp=f['remainingOriginalPlanPricePp'],additionalRemainingPp=f['additionalDiscoveredRemainingPp'],currentRevisedRemainingPp=f['revisedRemainingPp'])
for k in est:assert round(br['remainingCanonicalOriginalPricePp'][k]+br['additionalRemainingPp'][k]+br['historicalPartialAdjustmentPp'][k],3)==f['revisedRemainingPp'][k]
fp=d/'1636_WBS65予実・起動proof純八通常追加版417.json';wr(fp,f)
spec=b/'4264_起動proof原八・有限worker通常PT仕様.md';assert not spec.exists();spec.write_text('''# StartupProofFrame 原8件・有限worker通常PT仕様

NK-OPS-001、WBS-P018-03 / 費用WBS-F03追加資格 .3/.9/1.8pp上限3。SYS002/004・OPS009、UI212/251、SS341/342/343。BUG2865/YKT2387を修正前PG30066へ登録済み。Main変更なし、public値のparser/encoder/不変性だけ。

| Test ID | 元method / 独立期待値 |
|---|---|
| PT-OPS-PROOF-001 | proof001: Test手書きNKSTART1/17行ASCII・順序golden、個別値/固定redaction/proof_fd不含 |
| 002 | proof002: 17keyの欠落/未知/重複/順序/版/終端LF破損を拒否 |
| 003 | proof003: 非ASCII/制御byte・0/8192/8193・null引数/key/value/未知名。cloneによるborrowedinput不変 |
| 004 | proof004: literal pid/start/fd/u64/uidgid上下境界・overflow/非正準decimalを拒否 |
| 005 | proof005: 昇順unique群1..16、空/重複/逆順/0/overflow/17群を拒否 |
| 006 | proof006: API/WEB・非zero正準UUID/32hex・64lowerhex、固定hash比較 |
| 007 | proof007: 元Map消去/返却Map書換拒否/入力output消去後のsnapshot不変 |
| 008 | proof008: 独立32task/8workerで同手書きgoldenのparse→encode各byteをassert。Future各5秒、finally shutdownNow/await10秒・未終端fail |

元8のgolden/全期待値を保持。workerを有期限化するため実sourceを変更し、この変更後のwhole8だけを新しい単一runで実行。期待値をproduction methodから作らず、Testの固定textblock/境界literalを使用する。架空の権限を発行するものではなく、既存public Testに元からある非秘密値のbyte文法だけ。実Root/permit/FD/native/DB/VM/鍵/Backup/Unit/intent操作0、HOLD試験の抽出0。

全Main1+Bounds/Field計3physical、全Test1/元8定義をGJF→RootNullAway/lintWerror→PMD/Checkstyle/SpotBugs→適用性原票→preflight→Git source固定→一whole8→独立post。XML/FES/CRC/初期化/単一exec/全source四counterを照合。未達はそのまま保存し、manual除外・反射到達・無意味assert・旧exec合算なし。実JVM Code methodと既定JaCoCo generated filter差も別記。実行command/source/OS/JDK/tool/終了・input/output/hashは各manifest、結果文書に固定。全451/元190受入/実起動/生成code除外承認への転用なし。
''')
before=b/'evidence/PG30066-startup-proof8-worker-before-fix-v1/manifest.json';c=ld(i/'2432_backup_request9_profile.json');main='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/StartupProofFrame.java';test=main.replace('/main/','/test/').replace('Frame.java','FrameTest.java');classes=['dev/codex/schubert/nk/bootstrap/StartupProofFrame'+x for x in ['', '$Bounds','$Field']]
c.update(id='PG30086-STARTUP-PROOF-PURE8',productOwnerByMainPath={main:'WBS-P018-03'},oracleSpecs=[ref(spec)],closureProofs=[ref(before)],mainSources=[main],testSources=[dict(path=test,tests=8)],expectedTests=8,physicalClasses=[x+'.class' for x in classes],targetClasses=classes,pomInputs=['pom.xml','src/schubert-nk-bootstrap/pom.xml'],slots={k:str((b/f'evidence/PG{v}-startup-proof8-{k}-v1').relative_to(r)) for k,v in dict(prestyle=30078,prepare=30080,static=30082,preflight=30084,unit=30086,post=30088).items()},privateDirs=dict(prepare='pg30080-startup-proof8-prepare-v1',unit='pg30086-startup-proof8-unit-v1'),newTestDefinitions=0);wr(i/'2442_startup_proof8_profile.json',c)
start=ld(i/'2431_backup_request9_normal_start.json');start.update(groupId='PGPT-WBS65-STARTUP-PROOF-PURE-ORIGINAL8-FINITE-WORKER-NORMAL-20261114',recordPath=str((d/'1637_WBS65起動proof原八通常開始.json').relative_to(r)),scope='BUG2865 whole original StartupProofFrameTest8 finite pure JDK/value worker, oneMain+Bounds/Field3physical, original literal goldens unchanged; fullstatic/onefixedsourcewhole8/independentpost. No actual authority/extraction/RootFDVMDBnativekeypermitservice operations.',oracleRefs=[ref(spec),ref(before)],run=c['id'],estimate=est,capPp=3,workIds=['F03_BUG2865_STARTUP_PROOF_PURE_ORIGINAL8_NORMAL'],forecastRef=ref(fp),nextCommand='Finiteworkeronly submit32/Future5/finallyshutdownNow-await10, preserve all original8 literals/oracles. Prestyle then prepare static admission preflight fixedGit onewhole8 independent3CRC/init/counters; no quality credit until actual post. Continue other permitted PGPT beyond ordinaryunit/report.');wr(i/'2443_startup_proof8_start.json',start)
print(json.dumps(dict(actualExit=0,estimate=est,remaining=f['revisedRemainingPp'])))
