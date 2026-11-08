"""Reverse XML-to-trace join for Type catalog references, not a Java execution or acceptance."""
from pathlib import Path
from collections import Counter
import copy, datetime, hashlib, json, subprocess, xml.etree.ElementTree as E

R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'; S=B/'evidence/PG24730-typecatalog-method12-trace-v1'; O=B/'evidence/PG24732-typecatalog-method12-trace-independent-v1'
assert not O.exists()
load=lambda p:json.loads(p.read_bytes()); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=S/'manifest.json'; assert sha(mp)=='3834c90fe69c3f5089ed2e538c56ed70a742b00e8f1c081853146d282e224894'
m=load(mp); cfg=load(R/m['config']['path']); assert sha(R/m['config']['path'])==m['config']['sha256']
for n,h in m['files'].items():assert sha(S/n)==h
for ref in [cfg['normalProof'],cfg['metadataInventory'],cfg['descriptorInventory'],cfg['physicalIndex'],*cfg['oracleDocuments']]:assert sha(R/ref['path'])==ref['sha256']
normal=load(R/cfg['normalProof']['path']); parent=(R/cfg['normalProof']['path']).parent
assert normal['actualExit']==0 and normal['source']==cfg['testSource'] and normal['productionCoreMain']==cfg['source'] and normal['tests']==120
for n in ['coverage.xml','testcases.safe.xml']:assert sha(parent/n)==normal['files'][n]
scope=set(cfg['sourcePaths']); inv=[r for r in load(R/cfg['metadataInventory']['path']) if r['sourcePath'] in scope]; assert len(inv)==3
meta={r['physicalKey'].split(':',1)[1].removesuffix('.class'):r for r in inv}; ix=load(R/cfg['physicalIndex']['path']); desc={r['path']:r for r in load(R/cfg['descriptorInventory']['path']) if r['path'] in scope}
xml={r.get('name'):r for r in E.parse(parent/'coverage.xml').getroot().findall('.//class') if r.get('name') in meta}
expected={(n,x.get('name'),x.get('desc')):x for n,c in xml.items() for x in c.findall('method')}
rows=load(S/'method-trace.json'); cases=load(S/'case-oracles.json'); classes=load(S/'class-trace.json'); filtered=load(S/'standard-filter.json'); got={(r['className'],r['method'],r['descriptor']):r for r in rows}
assert len(rows)==len(got)==len(expected)==12 and got.keys()==expected.keys() and len(cases)==6
actual={r.get('classname')+'#'+r.get('name') for r in E.parse(parent/'testcases.safe.xml').getroot().findall('testcase')}; assert len(actual)==120
for label,c in cases.items():
 original=cfg['cases'][label]; assert c['caseKey']==original['caseKey'] and c['caseKey'] in actual and c['testIds']==original['testIds'] and c['independentOracle']==original['independentOracle'] and c['individualProbeAttribution'] is None
 p=R/c['path']; lines=p.read_text().splitlines(keepends=True); body=''.join(lines[c['declarationLine']-1:c['bodyEndLine']]); assert sha(p)==c['sourceSha256'] and hashlib.sha256(body.encode()).hexdigest()==c['assertionBodySha256'] and ('assert' in body or (label==cfg['delegatedCaseLabel'] and 'IndependentNamedFieldOracle.verifyAll();' in body))
 assert hashlib.sha256(subprocess.check_output(['git','show',cfg['testSource']+':'+c['path']])).hexdigest()==sha(p)
raw={(n,v['name'],v['descriptor']):v for n,r in meta.items() for v in r['structure']['methods']}; assert len(raw)==25
actual_filtered={(r['symbol'].split('#')[0],r['rawMetadata']['name'],r['rawMetadata']['descriptor']):r for r in filtered}
assert len(filtered)==len(actual_filtered)==13 and raw.keys()-expected.keys()==actual_filtered.keys()
assert Counter(k[0].split('/')[-1] for k in actual_filtered)==Counter({'PayloadTypeCatalog$Mapping':7,'PayloadTypeCatalog$RecordMapping':5,'PayloadTypeCatalog':1})
for key,r in actual_filtered.items():
 assert r['rawMetadata']==raw[key] and r['manualExclusion'] is False and r['artificialInvocation'] is False
 stem=key[0].split('/')[-1]
 if stem=='PayloadTypeCatalog':assert key[1:]==('<init>','()V') and raw[key]['flags']==2 and raw[key]['codeLength']==5 and 'UTILITY' in r['status']
 else:assert key[1] in cfg['generatedMethods'][stem] and 'RECORD' in r['status']
assert Counter(c['path'] for c in classes)==Counter(r['sourcePath'] for r in inv)
total={k:dict(covered=0,missed=0) for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}
for n,artifact in meta.items():
 path=artifact['sourcePath']; p=R/path; text=p.read_text(); assert artifact['owner']==desc[path]['owner']==desc[path]['costOwner']==cfg['owner'] and sha(p)==artifact['sourceSha256']==desc[path]['sha256'] and artifact['classSha256']==ix[n]['sha256']
 c=next(c for c in classes if c['className']==n); assert c['sourceSha256']==sha(p) and c['classSha256']==ix[n]['sha256'] and c['crc64']==ix[n]['crc64'] and c['owner']==c['costOwner']==cfg['owner']
 if n.endswith('/package-info'):
  assert not artifact['structure']['methods'] and n not in xml and c['status']=='ANNOTATION_ONLY_NO_METHOD_NO_CLASS_COVERAGE_CREDIT';continue
 ct={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml[n].findall('counter')}; assert c['counters']==ct and all(v['missed']==0 for v in ct.values())
 for k in total:
  for v in ['covered','missed']:total[k][v]+=ct.get(k,{}).get(v,0)
 for key in sorted(k for k in expected if k[0]==n):
  r=got[key]; rule=cfg['methodRules'][n.split('/')[-1]][key[1]]; xm=expected[key]
  assert r['sourcePath']==path and r['sourceSha256']==sha(p) and r['owner']==r['costOwner']==cfg['owner'] and r['firstExecutableLine']==int(xm.get('line'))
  for a,b in [('relatedRd','relatedRd'),('ssSections','ssSections'),('contract','contract'),('staticPath','staticPath'),('caseLabels','cases')]:assert r[a]==rule[b]
  assert r['actualCaseKeys']==[cases[l]['caseKey'] for l in rule['cases']] and r['testIdAliases']==sorted({i for l in rule['cases'] for i in cases[l]['testIds']}) and r['perCaseProbeAttribution'] is None and r['allBranchOraclesIndividuallyVerified'] is False
  assert r['methodCountersFromSame120Run']=={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xm.findall('counter')}
  if n.endswith('/PayloadTypeCatalog') and key[1] in ['decodeRecords','validateRecordTypes','require','mapping']:assert text.count(key[1]+'(')>1
helper=R/cfg['delegatedAssertionHelper']['path']; assert sha(helper)==cfg['delegatedAssertionHelper']['sha256'] and 'assertEquals' in helper.read_text() and 'static void verifyAll()' in helper.read_text();assert hashlib.sha256(subprocess.check_output(['git','show',cfg['testSource']+':'+str(helper.relative_to(R))])).hexdigest()==sha(helper)
assert total==m['coverageReferences'] and {k:total[k]['covered'] for k in total}==dict(LINE=176,METHOD=12,CLASS=3,BRANCH=18,INSTRUCTION=844)
# No exclusive RD ownership is assigned to P00102; MQ references remain shared.
task=next(r for r in load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks'] if r['id']==cfg['owner']); assert task['requirementIds']==[] and set(cfg['sourcePaths'])<=set(task['ownedArtifacts'])
assert all(set(rule['relatedRd'])<=set(['MQ-016','MQ-017']) for rules in cfg['methodRules'].values() for rule in rules.values())
sample=rows[0]
def row_contract(r):
 key=(r['className'],r['method'],r['descriptor']); reference=got[key]
 assert type(r['firstExecutableLine']) is int and r['firstExecutableLine']==reference['firstExecutableLine'] and r['owner']==r['costOwner']==cfg['owner'] and r['sourceSha256']==reference['sourceSha256'] and r['actualCaseKeys']==reference['actualCaseKeys'] and r['perCaseProbeAttribution'] is None and r['methodCountersFromSame120Run']==reference['methodCountersFromSame120Run']
checks=0
for field,value in [('descriptor','()Z'),('owner','WBS-P002-01'),('actualCaseKeys',['unknown#case()']),('sourceSha256','0'*64),('perCaseProbeAttribution',False),('firstExecutableLine',True),('methodCountersFromSame120Run',{})]:
 bad=copy.deepcopy(sample);bad[field]=value
 try:row_contract(bad)
 except (AssertionError,KeyError):checks+=1
 else:raise AssertionError('false Layout reference accepted')
for k,v in [('sourceArtifacts',1),('physicalClasses',3),('codeClasses',3),('annotationOnly',0),('rawMethods',25),('officialMeasuredMethods',12),('standardGeneratedFilters',13),('existingActualCaseKeys',6)]:assert type(m[k]) is int and m[k]==v
assert all(m[k]==0 for k in ['productTestsExecuted','newProductTests','newJavaCompilerExecutions','sourceRegistryAcceptedDelta','newAcceptance']) and m['formalUpdated'] is False and m['effortRate'] is None
priorRefs=[
 ('evidence/01_PT/018_NK-OPS-001/evidence/PG24694-layout-method25-trace-independent-v1/manifest.json','bc08487b765315335c646f1360a7873e3cf033e5f3eaf75b73404781dfcc8884'),
 ('evidence/01_PT/018_NK-OPS-001/evidence/PG24706-catalog-method33-trace-independent-v1/manifest.json','744f86cebafd04bdfa03e84abce393f467fc1a810dff4ade560fff5e20b1ca29'),
 ('evidence/01_PT/018_NK-OPS-001/evidence/PG24718-carrier-method14-trace-independent-v1/manifest.json','e272cdbeb727ed25ef38528fb683257f3ecd5be8bfd53dccc50ceab0795e031a')]
allSources=set(scope);allRows=list(rows);allClassNames=set(meta);allCases=set(c['caseKey'] for c in cases.values());allRaw=len(raw);allFilters=len(filtered);allAbstract=0;priorProofs=[]
for path,h in priorRefs:
 pm=R/path;assert sha(pm)==h;proof=load(pm);assert proof['actualExit']==0 and proof['newAcceptance']==0 and proof['source']==cfg['source'] and proof['testSource']==cfg['testSource'] and proof['perCaseProbeAttribution'] is None
 producer=R/proof['producerManifest']['path'];assert sha(producer)==proof['producerManifest']['sha256'];prod=load(producer)
 for n,hfile in prod['files'].items():assert sha(producer.parent/n)==hfile
 oldrows=load(producer.parent/'method-trace.json');oldclasses=load(producer.parent/'class-trace.json');oldcases=load(producer.parent/'case-oracles.json');oldSource={c['path'] for c in oldclasses};oldNames={c['className'] for c in oldclasses};assert not allSources&oldSource and not allClassNames&oldNames
 allSources|=oldSource;allClassNames|=oldNames;allRows+=oldrows;allCases|={c['caseKey'] for c in oldcases.values()};allRaw+=proof['rawMethods'];allFilters+=proof['standardGeneratedFilters'];allAbstract+=proof.get('abstractMethods',0);priorProofs.append(dict(path=path,sha256=sha(pm)))
assert allSources==set(task['ownedArtifacts']) and len(allSources)==20 and len(allClassNames)==29 and len(allRows)==84 and len(allCases)==16 and allRaw==174 and allFilters==85 and allAbstract==5
allInventory=[r for r in load(R/cfg['metadataInventory']['path']) if r['sourcePath'] in allSources];assert {r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in allInventory}==allClassNames
allXml={r.get('name'):r for r in E.parse(parent/'coverage.xml').getroot().findall('.//class') if r.get('name') in allClassNames};allExpected={(n,m.get('name'),m.get('desc')) for n,c in allXml.items() for m in c.findall('method')};assert len(allExpected)==84
assert {(r.get('className',r['symbol'].split('#')[0]),r.get('method',r['symbol'].split('#')[1].split('(',1)[0]),r.get('descriptor','('+r['symbol'].split('(',1)[1])) for r in allRows}==allExpected
allCounters={k:dict(covered=0,missed=0) for k in total}
for x in allXml.values():
 for k in allCounters:
  ct=x.find("counter[@type='"+k+"']")
  if ct is not None:
   for v in ['covered','missed']:allCounters[k][v]+=int(ct.get(v))
assert {k:v['covered'] for k,v in allCounters.items()}==dict(LINE=564,METHOD=84,CLASS=22,BRANCH=170,INSTRUCTION=3034) and all(v['missed']==0 for v in allCounters.values())
for item in allInventory:assert item['owner']==cfg['owner'] and sha(R/item['sourcePath'])==item['sourceSha256']
allSummary=dict(owner=cfg['owner'],sourceArtifacts=20,physicalClasses=29,officialMeasuredClasses=22,officialMeasuredMethods=84,rawMethods=174,standardGeneratedFilters=85,abstractMethods=5,actualExistingCaseRefs=16,scopeReferenceComplete=True,methodReferencesComplete=True,perCaseProbeAttribution=None,allBranchOraclesIndividuallyVerified=False,coverageReferences=allCounters,newRuntimeCoverage=False,newAcceptance=0,priorProofs=priorProofs,currentTypeCatalogProducer=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),sourcePaths=sorted(allSources),methodSymbols=sorted(r['symbol'] for r in allRows))
O.mkdir();(O/'p00102-all20-reference-summary.json').write_text(json.dumps(allSummary,ensure_ascii=False,indent=2)+'\n'); out=dict(ownerScopeArtifacts=20,ownerPhysicalClasses=29,ownerMeasuredMethods=84,ownerExistingCaseRefs=16,ownerReferenceSummarySha256=sha(O/'p00102-all20-reference-summary.json'),actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],testSource=cfg['testSource'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),sourceArtifacts=1,physicalClasses=3,codeClasses=3,annotationOnly=0,rawMethods=25,officialMeasuredMethods=12,standardGeneratedFilters=13,existingActualCaseKeys=6,coverageReferences=total,metadataNegativeChecks=checks,exclusiveRdOwnershipUnchanged=True,perCaseProbeAttribution=None,methodRelationsBoundOnly=True,allBranchOraclesIndividuallyVerified=False,productTestsExecuted=0,newProductTests=0,newJavaCompilerExecutions=0,sourceRegistryAcceptedDelta=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,methods=12,filters=13,cases=6,metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
