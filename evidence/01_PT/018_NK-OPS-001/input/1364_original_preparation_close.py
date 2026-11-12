"""Close original /1 preparation from explicit contracts; no /2 or acceptance credit."""
from pathlib import Path
import csv,datetime,hashlib,json,sys
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';D=R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';S=R.parent/'PMO/pgpt-completion-stage-20261102'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p))
a=load(Path(sys.argv[1]));start=load(R/a['startConfig']);mp=R/a['manifest'];m=load(mp);assert m['actualExit']==0 and m['wholeOwnSourceReviewed'] and m['productTestsExecuted']==m['newAcceptance']==0
w=start['wbsLeafIds'][0];assert m['completedOriginalPreparationWorkIds']==[w+'/1'];old=R/load(S/'checkpoint.json')['currentWbs65Forecast']['path'];f=load(old)
assert w+'/1' not in f['completedPlanWorkIds'];assert w+'/2' not in f['completedPlanWorkIds']
plan=R.parent/'PMO/hourly-monitor/execution-plan-20261110/65-前回の実績と初週の未達で予算を見直す条件/全領域で週20件のときの625行WBS.tsv'
rows={x['実行ID']:x for x in csv.DictReader(plan.open(encoding='utf-8-sig'),delimiter='\t')};row=rows[w+'/1'];both=[rows[w+'/1'],rows[w+'/2']]
for k,col in [('low','低位pp'),('base','標準pp'),('high','高位pp')]:
 x=float(row[col]);assert round(sum(float(r[col]) for r in both),3)==start['estimate'][k]
 f['completedPlanPriceSumPp'][k]=round(f['completedPlanPriceSumPp'][k]+x,3)
 for field in ['remainingOriginalPlanPricePp','revisedRemainingPp']:f[field][k]=round(f[field][k]-x,3)
f['previousForecast']=ref(old);f['revision']=a['revision'];f['atJST']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();f['completedPlanWorkIds'].append(w+'/1');f['completedPreparationWorkIds'].append(w+'/1');f['partiallyCompletedPlanWorkIds'].append(w)
for k in ['canonicalSchedulePricePrefixBasePp','startedRowPriceSumBasePp']:f[k]=round(f[k]+start['estimate']['base'],3)
f['remainingPriceAccountingNote']=a['description']+' Original /1 preparation only; /2/190/451 not accepted, source unchanged and no new PT.'
tech=dict(kind=w+'_ORIGINAL_PREPARATION_ONLY',evidence=ref(mp),ownSources=len(m['ownedSourceHashes']),MainOrTestChanged=False,productTestsExecuted=0,newAcceptance=0);f['latestGroupTechnicalResult']=tech
fp=D/a['forecastName'];assert not fp.exists();write(fp,f)
c=dict(groupId=start['groupId'],recordPath=str((D/a['resultName']).relative_to(R)),manifestPath=str(mp.relative_to(R)),manifestSha256=sha(mp),terminalAtUTC=m['atJST'],run=start['run'],workIds=start['workIds'],outcome=m['endingStatus'],technical=tech,forecastRef=ref(fp),nextCommand=a['nextCommand'],checkpointText=a['description']+' 原/1準備のみ完了、原/2未受入。版'+a['revision']+'残'+str(f['revisedRemainingPp'])+'未較正。元190新0/正式1964-53/工数null。')
out=B/'input'/a['endConfigName'];assert not out.exists();write(out,c)
pp=R/'evidence/01_PT/008_NK-SCN-001'/a['specName'];assert not pp.exists();lines=['# '+a['specTitle'],'','NK-SCN-001。対象source/hash、承認設計commit/hash、独立期待値/TestIDは ['+start['run']+'](../018_NK-OPS-001/'+str(mp.relative_to(B))+')。','']
for x in m['checks']:lines += ['- '+x['id']+' / '+x['methods']+' / '+','.join(x['testIds'])+': '+x['expected'],'']
lines += [a['description'],'','実行: `python3 -B '+a['auditCommand']+'` metadata終了0。新規製品PT/coverageなし。原/1の準備だけ、原/2・451・元190未受入。独立期待値は公開設計の固定境界・順序・後条件に基づき、production methodで生成しない。正式1964PT/53scope・工数null。',''];pp.write_text('\n'.join(lines))
for n in ['001_NK-SCN-001_単体テスト仕様書.md','002_NK-SCN-001_実行結果.md']:
 p=pp.parent/n;p.write_text(p.read_text()+'\n\n'+w+'公開source契約/独立期待値/TestIDは['+pp.name+']('+pp.name+')。metadataのみ、新PT/coverage/正式受入0。\n')
print(json.dumps(dict(forecast=ref(fp),remaining=f['revisedRemainingPp'],closeConfig=str(out.relative_to(R)))))
