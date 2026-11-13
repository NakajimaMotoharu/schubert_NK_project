"""Wire validated canonical counts into future closers/records; preserve exact previous sources."""
from pathlib import Path
import json,hashlib,ast
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';o=b/'evidence/PG29512-canonical-progress-caller-wiring-v1';assert not o.exists();o.mkdir();proof=[]
def patch(relative,pairs):
 p=r/relative;old=p.read_text();(o/(p.stem+'.before.py.txt')).write_text(old);new=old
 for a,z in pairs:assert new.count(a)==1,(relative,a);new=new.replace(a,z)
 ast.parse(new);inverse=new
 for a,z in reversed(pairs):assert inverse.count(z)==1;inverse=inverse.replace(z,a)
 assert inverse==old;p.write_text(new);proof.append(dict(path=relative,beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=hashlib.sha256(new.encode()).hexdigest(),wholeSourceInverseEqual=True,patchCount=len(pairs)))
p='evidence/01_PT/018_NK-OPS-001/input/1494b_original_multi_preparation_explicit_primary.py';anchor="sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();";insert="sys.path.insert(0,str(R/'tools/quality'))\nfrom pgpt_wbs_canonical_progress import validated_snapshot\n";a="tech=dict(kind=w+'_ORIGINAL_PREPARATION_ONLY'";z="f['canonical625Progress']=validated_snapshot(list(rows.values()),f,dict(path=str(plan),sha256=sha(plan)))\n"+a;patch(p,[(anchor,insert+anchor),(a,z)])
p='evidence/01_PT/018_NK-OPS-001/input/1100_wbs65_stage_record_v2.py';pairs=[];a='import pg998_metrics as metrics\n';pairs.append((a,'import csv\nfrom pgpt_wbs_canonical_progress import validated_snapshot\n'+a));a="if mode=='start' and forecast is not None:validate_forecast_additional_boundary(forecast)";z="""if forecast is not None and 'canonical625Progress' in forecast:
 plan_table=R.parent/'PMO/hourly-monitor/execution-plan-20261110/65-前回の実績と初週の未達で予算を見直す条件/全領域で週20件のときの625行WBS.tsv'
 with plan_table.open(encoding='utf-8-sig') as stream:canonical_rows=list(csv.DictReader(stream,delimiter='\\t'))
 assert forecast['canonical625Progress']==validated_snapshot(canonical_rows,forecast,dict(path=str(plan_table),sha256=sha(plan_table)))
"""+a;pairs.append((a,z));a=" event=metrics.append(group,'CHECKPOINT',values)";z=" if forecast is not None and 'canonical625Progress' in forecast:values['canonical625Progress']=forecast['canonical625Progress']\n"+a;pairs.append((a,z));a='out.parent.mkdir(parents=True,exist_ok=True);write(out,record)';z="if forecast is not None and 'canonical625Progress' in forecast:record['canonical625Progress']=forecast['canonical625Progress']\n"+a;pairs.append((a,z));a=' write(S/name,d)';z=" if forecast is not None and 'canonical625Progress' in forecast:d['currentCanonicalWbsProgress']=forecast['canonical625Progress']\n"+a;pairs.append((a,z));a=" text='\\n## 最新checkpoint（'";z=""" checkpoint_text=c['checkpointText']
 if forecast is not None and 'canonical625Progress' in forecast:
  counts=forecast['canonical625Progress']
  checkpoint_text+=' 正本WBS '+str(counts['uniqueCompletedRows'])+'/'+str(counts['canonicalRowCount'])+'行（/1='+str(counts['completedStage1Rows'])+'、/2='+str(counts['completedStage2Rows'])+'、単独='+str(counts['completedStandaloneRows'])+'）、legacy準備参照は完了行数/工数率にしない。'
 text='\\n## 最新checkpoint（'""";pairs.append((a,z));a="+c['checkpointText']+' event '";pairs.append((a,"+checkpoint_text+' event '"));patch(p,pairs)
m=dict(actualExit=0,pureMetadataCallerChanges=proof,MainOrTestChanged=False,productTestsExecuted=0,canonicalMasterRowChecks=625,oldLegacyArraysNotRewritten=True,oldPricesNotChanged=True,formalUpdate=False);(o/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('two caller deltas AST/inverse verified; future original/1 updates and group/checkpoint validate canonical counters')
