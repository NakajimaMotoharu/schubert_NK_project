"""Reverse-order, per-run provenance and set audit. No tests or application classes loaded."""
from pathlib import Path
import copy,datetime,hashlib,json,subprocess,xml.etree.ElementTree as E
R=Path.cwd();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
review=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG24432-current-target-set-review-v1/manifest.json';v=load(review);cfg=load(R/'evidence/01_PT/018_NK-OPS-001/input/714_current_target_scope.json');idx=load(R/cfg['normalIndex']);assert sha(R/cfg['normalIndex'])==cfg['indexSha256'];expected={'24282':(7,1,1),'24326':(32,4,5),'24352':(12,6,7),'24370':(64,11,24),'24396':(56,12,16),'24416':(28,0,0)}
def validate(x):
 assert type(x['actualExit']) is int and x['actualExit']==0 and x['productTestsExecuted']==0 and type(x['productTestsExecuted']) is int
 for k in ['mergedCoverage','sameFullRun','sourceSameForWholeFormal','formalUpdated']:assert x[k] is False
 assert x['newAcceptance']==0 and type(x['newAcceptance']) is int and x['effortRate'] is None
 assert x['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5' and len(x['groups'])==6
 refs=set();cases=set();physical=set();sources=set()
 for g in x['groups']:
  tag=g['reference']['tag'];assert tag in expected and tag not in refs;refs.add(tag);e=expected[tag];assert type(g['tests']) is int and g['tests']==e[0] and len(g['sources'])==e[1] and len(g['physical'])==e[2];c={(i['classname'],i['name']) for i in g['cases']};assert len(c)==len(g['cases'])==e[0] and not cases.intersection(c);assert not physical.intersection(g['physical']) and not sources.intersection(g['sources']);cases.update(c);physical.update(g['physical']);sources.update(g['sources'])
 assert len(cases)==199 and len(physical)==53 and len(sources)==34
validate(v);neg=[]
changes=[lambda x:x.update(actualExit=False),lambda x:x.update(productTestsExecuted=False),lambda x:x.update(mergedCoverage=True),lambda x:x.update(effortRate=0),lambda x:x['groups'][0]['cases'].append(x['groups'][0]['cases'][0]),lambda x:x['groups'][1].update(reference=x['groups'][0]['reference']),lambda x:x.update(formalUpdated=0),lambda x:x.update(productionCoreMain='0'*40)]
for change in changes:
 x=copy.deepcopy(v);before=json.dumps(x,sort_keys=True);change(x);assert json.dumps(x,sort_keys=True)!=before
 try:validate(x)
 except AssertionError:neg.append(True)
 else:raise AssertionError('negative accepted')
rootCounts={k:0 for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']};caseKeys=[];physical=[];sources=[];zeroSources=[];testPaths={};verified=[]
for g in reversed(v['groups']):
 ref=g['reference'];p=R/ref['path'];assert sha(p)==ref['sha256'];m=load(p);assert m['source']==g['source'] and m['tests']==expected[ref['tag']][0]
 if ref['tag']=='24416':cc={(i['classname'],i['name']) for i in m['testCases']};assert m['javaCoverage'] is None and m['snapshotCount']==82
 else:
  xml=p.parent/'coverage.xml';assert sha(xml)==m['files']['coverage.xml'];r=E.parse(xml).getroot();names=[c.get('name') for c in r.findall('.//class')];assert set(names)==set(g['physical']);sps={idx[n]['path'] for n in names};assert sps==set(g['sources']);assert all(idx[n]['sha256']==g['physical'][n] for n in names);physical.extend(names);sources.extend(sps)
  for k in rootCounts:
   counters=[c for c in r.findall('counter') if c.get('type')==k];assert len(counters)<=1;covered=0 if not counters else int(counters[0].get('covered'));missed=0 if not counters else int(counters[0].get('missed'));assert missed==0 and m['coverage'][k]==dict(covered=covered,missed=missed);rootCounts[k]+=covered
  for pkg in r.findall('package'):
   for sf in pkg.findall('sourcefile'):
    b=[c for c in sf.findall('counter') if c.get('type')=='BRANCH'];assert len(b)<=1
    if not b or int(b[0].get('covered'))+int(b[0].get('missed'))==0:zeroSources.append(pkg.get('name')+'/'+sf.get('name'))
  cc={(i['classname'],i['name'].removesuffix('()')) for i in m['caseTimings']}
 assert cc=={(i['classname'],i['name']) for i in g['cases']};caseKeys.extend(cc)
 for path,h in g['testSourceHashes'].items():assert sha(R/path)==h;testPaths[path]=h
 verified.append(dict(tag=ref['tag'],manifestSha256=sha(p),source=m['source'],cases=len(cc)))
assert len(caseKeys)==len(set(caseKeys))==199 and len(physical)==len(set(physical))==53 and len(sources)==len(set(sources))==34 and len(testPaths)==24;assert rootCounts==v['perRunCounterArithmetic']==dict(LINE=1242,METHOD=367,CLASS=53,BRANCH=470,INSTRUCTION=5785);assert len(zeroSources)==16
out=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG24434-current-target-set-independent-v1';assert not out.exists();out.mkdir();write(out/'manifest.json',dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain=v['productionCoreMain'],review=dict(path=str(review.relative_to(R)),sha256=sha(review)),postsVerified=verified,independentReverseSetAudit=True,metadataNegativeCases=len(neg),currentSourceHashesVerified=24,targetCodeSourcePrograms=34,targetCodePhysicalClasses=53,javaDistinctCases=171,domDistinctCases=28,allDistinctCases=199,perRunCounterArithmetic=rootCounts,naturalZeroBranchSourceCount=16,naturalZeroBranchSources=sorted(zeroSources),zeroBranchRate=None,metadataInterfaceNoCodeMethods=5,originalSixCoverageHoldPreserved=True,duplicateEarlierExecutions=6,historicalExecutionsInSubset=205,newExecutions=0,productTestsExecuted=0,newUniqueTests=0,sourceRegistryAcceptedDelta=0,oldExecUnion=False,mergedCoverage=False,sameFullRun=False,currentAllScopeAccepted=False,formalUpdated=False,newAcceptance=0,effortRate=None,allHoldsRetained=True,toolSha256=sha(__file__)));print(dict(actualExit=0,java=171,dom=28,source=34,physical=53,naturalZeroBranch=16,negative=8,manifestSha256=sha(out/'manifest.json')))
