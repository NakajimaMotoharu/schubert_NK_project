"""Price current-source raw gap partition without re-running any successful test."""
from pathlib import Path
from decimal import Decimal
import datetime, hashlib, json, subprocess
from pmo_forecast_bridge import reconcile_current_bridge
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106'
ld=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
wr=lambda p,v:p.open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
scope='Current Core7f04/Unit5b12 PG36280 whole145 original singleexec raw gap partition. Reuse PG36284 proven176physical/163Code/class hashes/CRC and raw methods, check relevant currentMain bytes against Core, enumerate exactly33 missing methods and59 missing branches with independent partition sums. Separate ten public value model contracts, six static utility responsibilities, string/enum condition branches and four compiler map gaps. Produce concrete next ordinary PT and SS-before-PG dependencies. No compilation, product execution, oldexec combination, new acceptance or current145 confirmation replay. All Root2 Actual4/VM/DB/native/aru/keys/private raw HOLD maintained.'
spec=b/'4429_現sourceProtocol残条件分割・証跡照合仕様.md'
spec.open('x').write('# 現sourceProtocol残条件分割・証跡照合仕様\n\n'+scope+'\n\nNK-PRO001002/UI231..236/SS322323354/451・BUG3111/YKT2583。期待値は元raw manifestのmethod/class/name/descriptorとcounter加算、現sourceのgit byte一致。COUNTは観測数でJUnit追加0。正式1964/53、WBS184/625、工数null不変。\n')
prior=next(d.glob('2439*'));f=ld(prior);budget=dict(low=.06,base=.18,high=.54)
f.update(revision='768-CURRENT_PROTOCOL_RAW_GAP_PARTITION_START',atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),previousForecast=ref(prior))
for k,v in budget.items():
 for key in ['additionalRequiredWorkGrossPp','additionalDiscoveredRemainingPp','revisedRemainingPp']:f[key][k]=float(Decimal(str(f[key][k]))+Decimal(str(v)))
f['currentFullForecastBudgetBridge']=reconcile_current_bridge(f)
fp=d/'2441_WBS65予実・現source残条件分割追加版768.json';wr(fp,f)
c=dict(groupId='PGPT-WBS65-CURRENT-PROTOCOL-RAW-GAP-PARTITION-20261116',recordPath=str((d/'2442_WBS65現source残条件分割開始.json').relative_to(r)),category='REVIEW',kind='SOURCE_REQUALIFICATION',scope=scope,oracleRefs=[ref(spec),ref(b/'evidence/PG36284-ssc445-registry-unfiltered-v2/manifest.json')],wbsLeafIds=['WBS-F03'],source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),run='PG36300-CURRENT-PROTOCOL-RAW-GAP-PARTITION',estimate=budget,capPp=.6,workIds=['CURRENT_PROTOCOL_RAW_GAP_PARTITION'],forecastRef=ref(fp),nextCommand='Partition33 method/59branch gaps with currentCore source byte guards and exact counter reconciliation; no product or compiler operation. Price the next coherent public value fixture and utility SS independently, keep global BUG3111/YKT2583 OPEN.')
wr(b/'input/4354_protocol_current_gap_start.json',c)
print(json.dumps(dict(actualExit=0,estimate=budget,productExecutions=0)))
