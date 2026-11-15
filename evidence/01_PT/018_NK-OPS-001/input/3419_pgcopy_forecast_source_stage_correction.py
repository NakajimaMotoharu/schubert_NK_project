"""BUG3005: preserve legacy/canonical preparation, separate new source-only stage."""
from pathlib import Path
import csv,hashlib,json,sys
r=Path.cwd();d=r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';i=r/'evidence/01_PT/018_NK-OPS-001/input';sys.path.insert(0,str(r/'tools/quality'));from pgpt_wbs_canonical_progress import validated_snapshot
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
old=next(d.glob('2092*'));f=load(old);start=load(next(d.glob('2089*')));wid='P01903_SSC417_PGJDBC_COPY_SOURCE_PT_SOURCE_REVIEW_HOLD';assert f['completedPreparationWorkIds']==start['completedPreparationWorkIds']+[wid]
f['completedPreparationWorkIds']=start['completedPreparationWorkIds'];f['sourceOnlyCompletedStages']=list(f.get('sourceOnlyCompletedStages',[]))+[dict(workId=wid,criteria='SOURCE_ONLY_REVIEW_NOT_PG_PT_ACCEPTANCE',plannedTests=24,actualTests=0,remainingPT='NOT_RUN_HOLD')]
f['revision']='605-PGCOPY_SOURCE_STAGE_NONCANONICAL_SEPARATE_BUG3005';f['forecastCorrection']=dict(bug='BUG3005',old=dict(path=str(old.relative_to(r)),sha256=sha(old)),reason='New source-stage record does not mutate legacy preparation/canonical completion. Initial end stopped before event; source unchanged.')
t=r.parent/'PMO/hourly-monitor/execution-plan-20261110/65-前回の実績と初週の未達で予算を見直す条件/全領域で週20件のときの625行WBS.tsv'
with t.open(encoding='utf-8-sig') as stream:rows=list(csv.DictReader(stream,delimiter='\t'))
assert f['canonical625Progress']==validated_snapshot(rows,f,dict(path=str(t),sha256=sha(t)))
assert f['revisedRemainingPp']==dict(low=397.324,base=837.386,high=1643.415)
p=d/'2094_WBS65予実・source段区分是正版605.json';write(p,f)
c=load(i/'3418_pgcopy_source_end.json');c.update(recordPath='documents/400_PGPT/470_PMO/600_通常PGPT_20261106/2095_WBS65PgJDBC COPY source段終了.json',forecastRef=dict(path=str(p.relative_to(r)),sha256=sha(p)));write(i/'3420_pgcopy_source_end_v2.json',c)
e=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG33712-pgcopy-source-only-limited-join-v1';write(e/'forecast-metadata-correction.json',dict(actualExit=0,bug='BUG3005',canonicalUnchanged=True,canonicalSnapshot=f['canonical625Progress'],sourceStageSeparate=True,additionalBudgetAddedPp=0,actualProductTests=0,oldFailedForecast=dict(path=str(old.relative_to(r)),sha256=sha(old)),correctedForecast=dict(path=str(p.relative_to(r)),sha256=sha(p))))
print(dict(actualExit=0,canonicalUnchanged=True,sourceOnlyStageSeparate=True))
