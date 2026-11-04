"""Historical shared-pool arithmetic only; never transfers old acceptance to current source."""
import json,hashlib,copy,os
from pathlib import Path
ROOT=Path.cwd();BASE=ROOT/'documents/400_PGPT/470_PMO/500_SV計画整備_20261104'
EVENTS=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
SEED=Path('/home/mini/codex/project1/work/PMO/hourly-monitor/completion-execution-kit-20261102/evidence/remaining-work-seed.json')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(doc,source):
 if doc['source']!=source:raise ValueError('wrong source slice')
 new=doc['newAcceptedIds'];rev=doc.get('revalidatedIds',doc.get('revalidatedDependencyIds',[]))
 if len(new)!=len(set(new)) or len(rev)!=len(set(rev)) or set(new)&set(rev):raise ValueError('duplicate/revalidation counted new')
 if set(new)|set(rev)!=set(doc['records']):raise ValueError('record identity inventory')
 if any(r['source']!=source or r['status']!='ACCEPTED' for r in doc['records'].values()):raise ValueError('source/status')
 return {'currentSourceAccepted':len(doc['records']),'newlyAccepted':len(new),'revalidated':len(rev)}
events=[]
for text in EVENTS.read_text().splitlines():
 e=json.loads(text);t=e.get('timeJST','')
 if e.get('eventType')=='ACCEPTANCE' and t.startswith('2026-10-23') and '06:00'<=t[11:16]<='10:30':events.append(e)
assert len(events)==6
docs=[];pins=[]
for e in events:
 refs=e['acceptedDelta']['evidenceRefs'];assert len(refs)==1
 r=refs[0];p=ROOT/r['path'];assert sha(p)==r['sha256'];doc=json.loads(p.read_text());assert e['source']==doc['source']
 calculated=validate(doc,e['source']);calculated['newThisStage']=len(e['acceptedDelta']['closedIds'])
 differences={k:{'historical':v,'expectedFromSetsAndEvent':calculated[k]} for k,v in doc.get('counting',{}).items() if k in calculated and v!=calculated[k]}
 docs.append({'eventId':e['eventId'],'atJST':e['timeJST'],'source':e['source'],'path':r['path'],'sha256':r['sha256'],'newIdsInThisEvent':e['acceptedDelta']['closedIds'],'cumulativeNewAcceptedIds':doc['newAcceptedIds'],'revalidatedIds':doc.get('revalidatedIds',doc.get('revalidatedDependencyIds',[])),'calculatedHistoricalCounts':calculated,'originalCountFieldsPreserved':doc.get('counting'),'correctionOverlay':differences,'originalByteUnchanged':True})
 pins.append((p,r['sha256']))
badRows=[r for r in docs if r['correctionOverlay']];assert len(badRows)==1 and badRows[0]['path'].endswith('/490_当source個別受入_C03追加.json')
assert badRows[0]['calculatedHistoricalCounts']=={'currentSourceAccepted':10,'newlyAccepted':6,'revalidated':4,'newThisStage':1}
sourceA='e7d64fda2453e906ee6ccc5fe718e5c29841e4aa';sourceB='3c70db39377cee751d7ecd12bb439c447e0c61c0'
a={k for r in docs if r['source']==sourceA for k in r['newIdsInThisEvent']};bb={k for r in docs if r['source']==sourceB for k in r['newIdsInThisEvent']}
assert len(a)==6 and bb=={'WBS-P020-01.01','WBS-P020-01.02','WBS-P020-01.03','WBS-P020-01'};b=bb-{'WBS-P020-01'}
assert len(a|b)==9 and not a&b
seed=json.loads(SEED.read_text());assert sha(SEED)=='90a6cada3c8081d2ee7c71b42b4a90640b8c3ea98fcda326e4b0f215b811f742'
pool=seed['reconstructedSharedCostEvidence']['reconstructedFullAcceptedEarlyBasket'];q=pool['interval'];assert q['reportedSharedDeltaPp']==q['toUsedPercent']-q['fromUsedPercent']==8 and q['reset']==1793306748
assert all(q['fromJST']<=r['atJST']<=q['toJST'] for r in docs)
originalDoc=json.loads(pins[0][0].read_text());negative=[]
for name,change in [('source',lambda x:x.update(source='0'*40)),('duplicate',lambda x:x['newAcceptedIds'].append(x['newAcceptedIds'][0])),('revalidationAsNew',lambda x:x['newAcceptedIds'].append(x['revalidatedIds'][0])),('missingRecord',lambda x:x['records'].pop(x['newAcceptedIds'][0])),('notAccepted',lambda x:x['records'][x['newAcceptedIds'][0]].update(status='OPEN'))]:
 bad=copy.deepcopy(originalDoc);change(bad)
 try:validate(bad,originalDoc['source'])
 except ValueError:negative.append(name)
 else:raise AssertionError(name)
for p,h in pins:assert sha(p)==h
out={'actualExit':0,'executionId':'PGPT-SV-20261104-01','pool':'S_POST_SAME10','scope':'HISTORICAL_ACCEPTANCE_COMPARISON_AND_ARITHMETIC_CORRECTION_NOT_CURRENT_ACCEPTANCE','sourceNow':'6b53efeec87f3ec36a840dd8e7759656cb4aee5c','seedSha256':sha(SEED),'historicalSourceSlices':docs,'newSourceALeaves':sorted(a),'newSourceBCurrentLeafChildren':sorted(b),'parentReferenceNotAdded':'WBS-P020-01','sourceAPrerequisiteRevalidations':['WBS-P001-01','WBS-P001-02','WBS-P002-03','WBS-C04'],'sourceBDependencyRevalidation':['WBS-F02'],'revalidationIsNotNew':True,'historicalSharedPool':pool,'historicalPoolCountedForComparison':1,'currentBudgetChargeForOldPool':0,'individualOrPerLeafUnitPrice':None,'futureFullCycleEstimatePp':{'low':None,'base':None,'high':None},'priceApplicability':'Already implemented proof reuse/config + limited common adapter/gate correction; Git e7->3c70 GateCli only12insert/3delete. Not comparable full unresolved Root/native/DB/current QA051 correlation contract. No divide8 by9 or13.','originalScalarDiscrepancies':badRows[0]['correctionOverlay'],'metadataNegativeVectors':negative,'BUG':'BUG2247','YKT':'YKT1993','newCurrentAcceptance':0,'newProductPT':0,'coverageAdded':0,'formalUpdated':False,'historical17NotIncremented':True,'effortCompletion':None,'forecastValidity':'PLAN_NOT_VALIDATED'}
p=BASE/'584_早期共有八pp受入量の原集合確認・集計追記訂正.json';assert not p.exists()
with p.open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':0,'oldSourceNewLeafContracts':9,'oldParentNotCounted':1,'originalCountCorrections':len(out['originalScalarDiscrepancies']),'sharedPoolObservedPp':8,'chargedToCurrentS':0,'metadataNegatives':len(negative),'newCurrentAcceptance':0,'sha256':sha(p)}))
