"""Explicit original artifact review records; no product calls or acceptance/coverage claims."""
from pathlib import Path
import csv,datetime,hashlib,json,subprocess,sys
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';D=R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';S=R.parent/'PMO/pgpt-completion-stage-20261102';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));wr=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n');mode,config=sys.argv[1:];a=ld(Path(config));leaves=a.get('canonicalCostLeafIds',[a['taskId']]);assert 1<=len(leaves)<=4 and len(set(leaves))==len(leaves);task=next(x for x in ld(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks'] if x['id']==a['taskId']);ck=ld(S/'checkpoint.json');now=datetime.datetime.now().astimezone().isoformat()
owned_paths=task['ownedArtifacts'];projection=None
if 'currentOwnedProjection' in a:
 sys.path.insert(0,str(R/'tools/quality'))
 from wbs_current_source_structure import pinned_public_json,preparation_projection,value_digest
 cfg=a['currentOwnedProjection'];inv=ld(R/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json');master=ld(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json');view=inv['currentSourceArtifactStructureView20261108']
 assert cfg['viewValueDigest']==value_digest(view) and cfg['productionCoreMain']==ck['productionCoreMain']
 frozen=pinned_public_json(R,cfg['legacyRows']);base=pinned_public_json(R,view['descriptorBase'])
 names=subprocess.check_output(['git','ls-tree','-r','--name-only',view['source'],'--','src','program/characterization/src/main/java'],text=True).splitlines()
 projection=preparation_projection(view,base,frozen,inv['artifacts'],master['tasks'],names,task['id'],cfg['registeredAdditions'])
 assert projection['paths']==cfg['expectedOwnedPaths']
 owned_paths=projection['paths']
 for name in owned_paths:
  assert sha(R/name)==hashlib.sha256(subprocess.check_output(['git','show',cfg['productionCoreMain']+':'+name])).hexdigest()
 projection.update(legacyRows=cfg['legacyRows'],viewValueDigest=cfg['viewValueDigest'],historicalTaskOwnedPaths=task['ownedArtifacts'],sourceCoreMain=cfg['productionCoreMain'],currentSourceHashesBoundToCore=True)
if mode=='start':
 sys.path.insert(0,str(R/'tools/quality'))
 from pgpt_preparation_price_bridge import preparation_deduction
 current=ld(R/ck['currentWbs65Forecast']['path'])
 for leaf in leaves:
  import csv as price_csv
  price_plan=R.parent/'PMO/hourly-monitor/execution-plan-20261110/65-前回の実績と初週の未達で予算を見直す条件/全領域で週20件のときの625行WBS.tsv'
  row=next(x for x in price_csv.DictReader(price_plan.open(encoding='utf-8-sig'),delimiter='\t') if x['実行ID']==leaf+'/1')
  preparation_deduction(current,leaf,{k:float(row[col]) for k,col in [('low','低位pp'),('base','標準pp'),('high','高位pp')]})
 plan=R.parent/'PMO/hourly-monitor/execution-plan-20261110/65-前回の実績と初週の未達で予算を見直す条件/全領域で週20件のときの625行WBS.tsv';rows=[x for x in csv.DictReader(plan.open(encoding='utf-8-sig'),delimiter='\t') if x['実行ID'] in [leaf+'/'+str(n) for leaf in leaves for n in [1,2]]];assert len(rows)==2*len(leaves);price={k:round(sum(float(x[c]) for x in rows),3) for k,c in [('low','低位pp'),('base','標準pp'),('high','高位pp')]};o=R/a['startConfig'];assert not o.exists();c=dict(groupId=a['groupId'],recordPath=str((D/a['startRecord']).relative_to(R)),category='CONTRACT_AUDIT',kind='ORIGINAL_PLAN',scope=a['scope'],oracleRefs=[ref(R/p) for p in a['oraclePaths']],wbsLeafIds=leaves,source=ck['productionCoreMain'],run=a['run'],estimate=price,capPp=a.get('capPp',2),workIds=[leaf+'/'+str(n) for leaf in leaves for n in [1,2]],forecastRef=ck['currentWbs65Forecast'],nextCommand=a['nextCommand']);wr(o,c);print(dict(actualExit=0,estimate=price));raise SystemExit(0)
assert mode=='audit';start=ld(R/a['startConfig']);assert ck['ordinaryActiveGroup']==start['groupId'];own={p:sha(R/p) for p in owned_paths};assert len(own)==a['expectedOwned'];commit=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();design=[]
for base,prefix in a['designPrefixes']:
 p=next((R/base).glob('**/'+prefix+'*.md'));data=subprocess.check_output(['git','show',commit+':'+str(p.relative_to(R))]);design.append(dict(path=str(p.relative_to(R)),commit=commit,sha256=hashlib.sha256(data).hexdigest()))
proof=[]
for item in a.get('existingProofs',[]):
 p=R/item['manifest'];m=ld(p);assert m['actualExit']==0 and m['tests']==item['tests'];assert all(sha(R/name)==m['inputHashes'][name] for name in item['unchangedInputPaths']);proof.append(dict(manifest=ref(p),oldSource=m['source'],oldScopeOnly=item['oldScopeOnly'],unchangedInputPaths=item['unchangedInputPaths'],reexecuted=0,currentWholeScopeTransferred=False))
o=B/'evidence'/a['manifestDirectory'];assert not o.exists();o.mkdir();v=dict(actualExit=0,atJST=now,source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain=start['source'],ownedSourceHashes=own,currentOwnedProjection=projection,wholeOwnSourceReviewed=True,ownedLines=sum(len((R/p).read_text().splitlines()) for p in own),design=design,checks=a['checks'],existingProofs=proof,internalDependencies=task['dependencies'],completedOriginalPreparationWorkIds=[leaf+'/1' for leaf in leaves],endingStatus=a['endingStatus'],productTestsExecuted=0,newDefinitions=0,MainOrTestChanged=False,newAcceptance=0,formalUpdated=False,effortRate=None,actualHeldClassBinaryActions=0,verifier=ref(Path(__file__).resolve()),explicitReviewConfig=ref(Path(config).resolve()));wr(o/'manifest.json',v);print(json.dumps(dict(actualExit=0,owned=len(own),lines=v['ownedLines'],manifest=ref(o/'manifest.json'))))
