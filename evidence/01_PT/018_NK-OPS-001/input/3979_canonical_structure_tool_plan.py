"""Necessary metadata collector repair; no WBS budgets or historical events rewritten."""
from pathlib import Path
from decimal import Decimal
import datetime,hashlib,json,subprocess
from pmo_forecast_bridge import reconcile_current_bridge
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));wr=lambda p,v:p.open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
scope='BUG3084/YKT2557: canonical481/484 actual structure276 tasks/children/sharedBudgets only, no recursive historical id overwrite. Repair pmo_group_context.collect_canonical_nodes and pg998_metrics.append reader; preserve parent-child structure, reject duplicate structural ids, unknown/colon/nonleaf, validate actualCleanupKind owner to real01707.02 descendant. Independent tool-only unit tests and actual public-plan snapshot, no event replay or original625/190/cost/formal changes. Current batch carry.05/.15/.45 retained separately, tool additional.05/.15/.45 cap.5, no app/source/binary/backend operation.'
spec=b/'4359_WBS構造収集・履歴分離工具仕様.md';spec.open('x').write('# WBS構造収集・履歴分離 工具仕様\n\n'+scope+'\n\n期待値は既定top-level276構造node集合・481P01707明示三children/484子parent文字列、履歴内同IDは影響0。実装へ元費再割当0/工具試験を製品PTへ算入0。487/BUG3084/YKT2557。\n')
prior=next(d.glob('2293*'));f=ld(prior);budget=dict(low=.05,base=.15,high=.45);f.update(revision='699-CANONICAL_STRUCTURE_TOOL_START',atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),previousForecast=ref(prior))
for k,v in budget.items():
 for key in ['additionalRequiredWorkGrossPp','additionalDiscoveredRemainingPp','revisedRemainingPp']:f[key][k]=float(Decimal(str(f[key][k]))+Decimal(str(v)))
f['currentFullForecastBudgetBridge']=reconcile_current_bridge(f);fp=d/'2295_WBS65予実・WBS構造工具追加版699.json';wr(fp,f)
cfg=dict(groupId='PGPT-WBS65-CANONICAL-STRUCTURE-TOOL-20261116',recordPath=str((d/'2296_WBS65WBS構造工具開始.json').relative_to(r)),category='REVIEW',kind='TOOL_FIX',scope=scope,oracleRefs=[ref(spec)],wbsLeafIds=['WBS-F03'],source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),run='PG35040-CANONICAL-STRUCTURE-TOOL',estimate=budget,capPp=.5,workIds=['CANONICAL_STRUCTURE_TOOL'],forecastRef=ref(fp),nextCommand='Repair only canonical structure readers and independent metadata tests. No app run or history rewrite. ResumeSSC437 branch repair afterwards with unchangedcarry.')
wr(b/'input/3980_canonical_structure_tool_start.json',cfg);print(json.dumps(dict(actualExit=0,estimate=budget,productActions=0)))
