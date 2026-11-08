"""Independent reverse19 JVM signatures/case/requirement-owner references; no runtime tests."""
from pathlib import Path
from collections import Counter
import json,hashlib,xml.etree.ElementTree as E,re,datetime,copy
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=B/'evidence/PG24660-field-three-method19-trace-v1';O=B/'evidence/PG24662-field-three-method19-trace-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();mp=S/'manifest.json';assert sha(mp)=='4f1c962b29e534561bf92ca65037d4552583a384a33ee1b9711d9cd26fc8d5d2';m=load(mp);cp=R/m['config']['path'];assert sha(cp)==m['config']['sha256'];cfg=load(cp)
for n,h in m['files'].items():assert sha(S/n)==h
rows=load(S/'method-trace.json');cases=load(S/'case-oracles.json');classes=load(S/'class-trace.json');filtered=load(S/'standard-filter.json');assert len(rows)==19 and len(cases)==10 and len(classes)==3 and len(filtered)==1
for r in [cfg['normalProof'],cfg['oracleQualification'],cfg['metadataInventory'],cfg['descriptorInventory'],cfg['physicalIndex'],*cfg['oracleDocuments']]:assert sha(R/r['path'])==r['sha256']
normal=load(R/cfg['normalProof']['path']);assert normal['actualExit']==0 and normal['tests']==120 and normal['newIndependentCauseCasePassed'] is True and normal['source']==cfg['testSource'] and normal['productionCoreMain']==cfg['source'];parent=(R/cfg['normalProof']['path']).parent;root=E.parse(parent/'coverage.xml').getroot();actualCases={t.get('classname')+'#'+t.get('name') for t in E.parse(parent/'testcases.safe.xml').getroot().findall('testcase')};assert len(actualCases)==120
ix=load(R/cfg['physicalIndex']['path']);inv=load(R/cfg['metadataInventory']['path']);desc={r['path']:r for r in load(R/cfg['descriptorInventory']['path'])};wbs={r['id']:r for r in load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks']};meta={r['physicalKey'].split(':',1)[1].removesuffix('.class'):r for r in inv if r['sourcePath'] in cfg['sourcePaths']};assert len(meta)==3
xml={r.get('name'):r for r in root.findall('.//class') if r.get('name') in meta};expected={(name,method.get('name'),method.get('desc')):method for name,c in xml.items() for method in c.findall('method')};by={(r['symbol'].split('#')[0],r['symbol'].split('#')[1].split('(',1)[0],'('+r['symbol'].split('(',1)[1]):r for r in rows};assert set(by)==set(expected) and len(by)==19
for label,c in cases.items():
 assert c['caseKey']==cfg['cases'][label]['caseKey'] and c['caseKey'] in actualCases and c['testIds']==cfg['cases'][label]['testIds'] and c['independentOracle']==cfg['cases'][label]['independentOracle'] and c['individualProbeAttribution'] is None
 p=R/c['path'];assert sha(p)==c['sourceSha256'];lines=p.read_text().splitlines(keepends=True);body=''.join(lines[c['declarationLine']-1:c['bodyEndLine']]);assert hashlib.sha256(body.encode()).hexdigest()==c['assertionBodySha256'] and c['caseKey'].split('#')[1].removesuffix('()') in body and 'assert' in body
sourceText={};bodies={}
for name,item in meta.items():
 path=item['sourcePath'];artifact=desc[path];actualOwner=cfg['sourceOwners'][path];assert actualOwner==artifact['owner']==artifact['costOwner']==item['owner'];assert sha(R/path)==item['sourceSha256']==artifact['sha256'];assert item['classSha256']==ix[name]['sha256'];sourceText[name]=(R/path).read_text().splitlines(keepends=True)
 for key,xm in expected.items():
  if key[0]!=name:continue
  line=int(xm.get('line'))-1;end=next(n for n in range(line,len(sourceText[name])) if sourceText[name][n]=='  }\n');bodies[key]=''.join(sourceText[name][line:end+1])
for key in sorted(by,reverse=True):
 r=by[key];item=meta[key[0]];path=item['sourcePath'];own=cfg['sourceOwners'][path];ruleKey=key[1] if key[1]!='<init>' else Path(path).stem+'#'+key[2];rule=cfg['methodRules'][ruleKey];assert r['owner']==r['costOwner']==own and r['sourcePath']==path and r['sourceSha256']==desc[path]['sha256'] and r['firstExecutableLine']==int(expected[key].get('line'))
 assert r['relatedRd']==rule['relatedRd'] and r['ssSections']==rule['ssSections'] and r['methodContract']==rule['contract'] and r['caseLabels']==rule['cases'] and r['callerMethods']==rule['callerMethods'];assert r['sharedRdReferences']==[v for v in r['relatedRd'] if v not in wbs[own]['requirementIds']]
 assert r['actualCaseKeys']==[cases[c]['caseKey'] for c in rule['cases']] and 0<len(r['actualCaseKeys'])<=10 and set(r['actualCaseKeys'])<=actualCases and r['testIdAliases']==sorted({v for c in rule['cases'] for v in cases[c]['testIds']})
 assert r['perCaseProbeAttribution'] is None and r['branchOracleCompleteNotClaimed'] is True and r['methodObservedInWhole120'] is True
 counters={c.get('type'):dict(covered=int(c.get('covered')),missed=int(c.get('missed'))) for c in expected[key].findall('counter')};assert r['methodCountersFromSame120Run']==counters and all(c['missed']==0 for c in counters.values()) and counters['METHOD']['covered']==1
 # Scope-specific source edge check anchored by existing official line metadata, not a new Java parser.
 if rule['callerMethods']:
  for caller in rule['callerMethods']:
   callerKey=next(k for k in bodies if k[0].endswith('/FieldCodec') and k[1]==caller);token=key[1]+'(' if key[1]!='<init>' else 'new '+Path(path).stem+'(';assert token in bodies[callerKey]
 else:
  assert key[0].endswith('/FieldCodec') and any(('FieldCodec.'+key[1]+'(') in ''.join((R/cases[c]['path']).read_text().splitlines(keepends=True)[cases[c]['declarationLine']-1:cases[c]['bodyEndLine']]) for c in rule['cases'])
assert Counter(r['owner'] for r in rows)==Counter({'WBS-P002-01':17,'WBS-P002-04':2}) and Counter(r['owner'] for r in classes)==Counter({'WBS-P002-01':2,'WBS-P002-04':1})
f=filtered[0];assert f['symbol'].endswith('/FieldCodec#<init>()V') and f['rawMetadata']['flags']==2 and f['rawMetadata']['codeLength']==5 and f['manualExclusion'] is False and f['artificialInvocation'] is False
for path,r in m['approvedDesigns'].items():assert sha(R/path)==r['sha256']
# False-owner/phantom-case/individual-probe/descriptor mutations must fail even if Python bool==int.
def rowContract(r):
 name=r['symbol'].split('#')[0];path=meta[name]['sourcePath'];assert r['sourcePath']==path and r['owner']==r['costOwner']==cfg['sourceOwners'][path] and r['perCaseProbeAttribution'] is None
 key=next(k for k in by if by[k]['symbol']==r['symbol']);ref=by[key];assert r['actualCaseKeys']==ref['actualCaseKeys'] and r['relatedRd']==ref['relatedRd'] and r['sourceSha256']==ref['sourceSha256'] and r['firstExecutableLine']==ref['firstExecutableLine'] and type(r['firstExecutableLine']) is int
sample=next(r for r in rows if r['owner']=='WBS-P002-04');checks=0
for field,value in [('owner','WBS-P002-01'),('costOwner','WBS-P002-01'),('perCaseProbeAttribution',False),('actualCaseKeys',['unknown#case()']),('relatedRd',[]),('sourceSha256','0'*64),('firstExecutableLine',True)]:
 bad=copy.deepcopy(sample);bad[field]=value;assert json.dumps(bad,sort_keys=True)!=json.dumps(sample,sort_keys=True)
 try:rowContract(bad)
 except (AssertionError,KeyError,StopIteration):checks+=1
 else:raise AssertionError('false trace relation')
for name,old in [('sourcePrograms',3),('officialMeasuredMethods',19),('rawMethods',20),('existingActualCaseKeys',10)]:assert type(m[name]) is int and m[name]==old
assert m['wholeG13Accepted'] is False and m['whole451Accepted'] is False and m['productTestsExecuted']==m['newProductTests']==m['newJavaCompilerExecutions']==0 and m['perCaseProbeAttribution'] is None
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=m['observerSource'],source=cfg['source'],productionCoreMain=cfg['source'],testSource=cfg['testSource'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),normalProof=cfg['normalProof'],sourcePrograms=3,physicalClasses=3,rawMethods=20,officialMeasuredMethods=19,standardFilteredPrivateConstructors=1,existingActualCaseKeys=10,measuredMethodOwnerCounts={'WBS-P002-01':17,'WBS-P002-04':2},sourceOwnerCounts={'WBS-P002-01':2,'WBS-P002-04':1},metadataNegativeChecks=checks,staticCallerAndCaseEdgesVerified=True,perCaseProbeAttribution=None,methodRelationsBoundOnly=True,allBranchOraclesIndividuallyVerified=False,coverageReferences=m['coverageReferences'],productTestsExecuted=0,newProductTests=0,newJavaCompilerExecutions=0,heldFourInitializations=0,sourceRegistryAcceptedDelta=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,toolSha256=sha(Path(__file__)));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sources=3,methods=19,cases=10,metadataNegatives=checks,manifestSha256=sha(O/'manifest.json'))))
