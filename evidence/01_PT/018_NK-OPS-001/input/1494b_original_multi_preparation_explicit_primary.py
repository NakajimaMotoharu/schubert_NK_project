"""Close original /1 preparation from explicit contracts; no /2 or acceptance credit."""
from pathlib import Path
import csv,datetime,hashlib,json,sys
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';D=R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';S=R.parent/'PMO/pgpt-completion-stage-20261102'
sys.path.insert(0,str(R/'tools/quality'))
from pgpt_wbs_canonical_progress import validated_snapshot
from pgpt_preparation_price_bridge import preparation_deduction
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p))
a=load(Path(sys.argv[1]));primary=a.get('primaryDocumentNames');
if primary is not None:
 assert len(primary)==2 and len(set(primary))==2 and all('/' not in x and x.endswith('.md') for x in primary)
 assert primary[0].startswith('001_'+a['programId']+'_') and primary[1].startswith('002_'+a['programId']+'_')
 assert all((R/'evidence/01_PT'/a['programDirectory']/x).is_file() for x in primary)
start=load(R/a['startConfig']);mp=R/a['manifest'];m=load(mp);assert m['actualExit']==0 and m['wholeOwnSourceReviewed'] and m['productTestsExecuted']==m['newAcceptance']==0
leaves=start['wbsLeafIds'];assert 1<=len(leaves)<=4;work=[v+'/1' for v in leaves];assert m['completedOriginalPreparationWorkIds']==work;w=','.join(leaves);old=R/load(S/'checkpoint.json')['currentWbs65Forecast']['path'];f=load(old)
assert all(v not in f['completedPlanWorkIds'] for v in work) and all(v+'/2' not in f['completedPlanWorkIds'] for v in leaves)
plan=R.parent/'PMO/hourly-monitor/execution-plan-20261110/65-前回の実績と初週の未達で予算を見直す条件/全領域で週20件のときの625行WBS.tsv'
rows={x['実行ID']:x for x in csv.DictReader(plan.open(encoding='utf-8-sig'),delimiter='\t')};prepared=[rows[v] for v in work];both=[rows[v+'/'+str(n)] for v in leaves for n in [1,2]]
deductions=[preparation_deduction(f,leaf,{k:float(rows[leaf+'/1'][col]) for k,col in [('low','低位pp'),('base','標準pp'),('high','高位pp')]}) for leaf in leaves]
for k,col in [('low','低位pp'),('base','標準pp'),('high','高位pp')]:
 x=round(sum(float(v[col]) for v in prepared),3);assert round(sum(float(r[col]) for r in both),3)==start['estimate'][k]
 f['completedPlanPriceSumPp'][k]=round(f['completedPlanPriceSumPp'][k]+x,3)
 f['remainingOriginalPlanPricePp'][k]=round(f['remainingOriginalPlanPricePp'][k]-x,3)
 f['revisedRemainingPp'][k]=round(f['revisedRemainingPp'][k]-sum(item[k] for item in deductions),3)
f['previousForecast']=ref(old);f['revision']=a['revision'];f['atJST']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();f['completedPlanWorkIds'].extend(work);f['completedPreparationWorkIds'].extend(work);f['partiallyCompletedPlanWorkIds'].extend(leaves)
for k in ['canonicalSchedulePricePrefixBasePp','startedRowPriceSumBasePp']:f[k]=round(f[k]+start['estimate']['base'],3)
f['remainingPriceAccountingNote']=a['description']+' Original /1 preparation only; /2/190/451 not accepted, source unchanged and no new PT.'
f['canonical625Progress']=validated_snapshot(list(rows.values()),f,dict(path=str(plan),sha256=sha(plan)))
tech=dict(kind=w+'_ORIGINAL_PREPARATION_ONLY',evidence=ref(mp),ownSources=len(m['ownedSourceHashes']),MainOrTestChanged=False,productTestsExecuted=0,newAcceptance=0);f['latestGroupTechnicalResult']=tech
fp=D/a['forecastName'];assert not fp.exists();write(fp,f)
c=dict(groupId=start['groupId'],recordPath=str((D/a['resultName']).relative_to(R)),manifestPath=str(mp.relative_to(R)),manifestSha256=sha(mp),terminalAtUTC=m['atJST'],run=start['run'],workIds=start['workIds'],outcome=m['endingStatus'],technical=tech,forecastRef=ref(fp),nextCommand=a['nextCommand'],checkpointText=a['description']+' 原/1準備のみ完了、原/2未受入。版'+a['revision']+'残'+str(f['revisedRemainingPp'])+'未較正。元190新0/正式1964-53/工数null。')
out=B/'input'/a['endConfigName'];assert not out.exists();write(out,c)
program=a.get('programId','NK-SCN-001');directory=a.get('programDirectory','008_NK-SCN-001');assert directory.endswith('_'+program) and '/' not in directory;programRoot=R/'evidence/01_PT'/directory;assert programRoot.is_dir();pp=programRoot/a['specName'];assert not pp.exists();lines=['# '+a['specTitle'],'',program+'。対象source/hash、承認設計commit/hash、独立期待値/TestIDは ['+start['run']+'](../018_NK-OPS-001/'+str(mp.relative_to(B))+')。','']
for x in m['checks']:lines += ['- '+x['id']+' / '+x['methods']+' / '+','.join(x['testIds'])+': '+x['expected'],'']
lines += [a['description'],'','実行: `python3 -B '+a['auditCommand']+'` metadata終了0。新規製品PT/coverageなし。原/1の準備だけ、原/2・451・元190未受入。独立期待値は公開設計の固定境界・順序・後条件に基づき、production methodで生成しない。正式1964PT/53scope・工数null。',''];pp.write_text('\n'.join(lines))
for n in a.get('primaryDocumentNames',['001_'+program+'_単体テスト仕様書.md','002_'+program+'_実行結果.md']):
 p=pp.parent/n;p.write_text(p.read_text()+'\n\n'+w+'公開source契約/独立期待値/TestIDは['+pp.name+']('+pp.name+')。metadataのみ、新PT/coverage/正式受入0。\n')
print(json.dumps(dict(forecast=ref(fp),remaining=f['revisedRemainingPp'],closeConfig=str(out.relative_to(R)))))
