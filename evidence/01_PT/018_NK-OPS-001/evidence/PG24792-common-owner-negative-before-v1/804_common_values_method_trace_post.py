"""Reverse XML-to-trace join for Common value references, not a Java execution or acceptance."""
from pathlib import Path
from collections import Counter
import copy, datetime, hashlib, json, subprocess, xml.etree.ElementTree as E

R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'; S=B/'evidence/PG24788-common41-method104-trace-v1'; O=B/'evidence/PG24790-common41-method104-trace-independent-v1'
assert not O.exists()
load=lambda p:json.loads(p.read_bytes()); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=S/'manifest.json'; assert sha(mp)=='0796a832698354945f1e77cd01bf9f9e3e07d6b24cdbc6bd3c09668c11ddfda3'
m=load(mp); cfg=load(R/m['config']['path']); assert sha(R/m['config']['path'])==m['config']['sha256']
for n,h in m['files'].items():assert sha(S/n)==h
for ref in [cfg['normalProof'],cfg['metadataInventory'],cfg['descriptorInventory'],cfg['physicalIndex'],*cfg['oracleDocuments']]:assert sha(R/ref['path'])==ref['sha256']
normal=load(R/cfg['normalProof']['path']); parent=(R/cfg['normalProof']['path']).parent
assert normal['actualExit']==0 and normal['source']==cfg['testSource'] and normal['productionCoreMain']==cfg['source'] and normal['tests']==120
for n in ['coverage.xml','testcases.safe.xml']:assert sha(parent/n)==normal['files'][n]
scope=set(cfg['sourcePaths']); inv=[r for r in load(R/cfg['metadataInventory']['path']) if r['sourcePath'] in scope]; assert len(inv)==41
meta={r['physicalKey'].split(':',1)[1].removesuffix('.class'):r for r in inv}; ix=load(R/cfg['physicalIndex']['path']); desc={r['path']:r for r in load(R/cfg['descriptorInventory']['path']) if r['path'] in scope}
xml={r.get('name'):r for r in E.parse(parent/'coverage.xml').getroot().findall('.//class') if r.get('name') in meta}
expected={(n,x.get('name'),x.get('desc')):x for n,c in xml.items() for x in c.findall('method')}
rows=load(S/'method-trace.json'); cases=load(S/'case-oracles.json'); classes=load(S/'class-trace.json'); filtered=load(S/'standard-filter.json'); got={(r['className'],r['method'],r['descriptor']):r for r in rows}
assert len(rows)==len(got)==len(expected)==104 and got.keys()==expected.keys() and len(cases)==7
actual={r.get('classname')+'#'+r.get('name') for r in E.parse(parent/'testcases.safe.xml').getroot().findall('testcase')}; assert len(actual)==120
for label,c in cases.items():
 original=cfg['cases'][label]; assert c['caseKey']==original['caseKey'] and c['caseKey'] in actual and c['testIds']==original['testIds'] and c['independentOracle']==original['independentOracle'] and c['individualProbeAttribution'] is None
 p=R/c['path']; lines=p.read_text().splitlines(keepends=True); body=''.join(lines[c['declarationLine']-1:c['bodyEndLine']]); assert sha(p)==c['sourceSha256'] and hashlib.sha256(body.encode()).hexdigest()==c['assertionBodySha256'] and 'assert' in body
 assert hashlib.sha256(subprocess.check_output(['git','show',cfg['testSource']+':'+c['path']])).hexdigest()==sha(p)
raw={(n,v['name'],v['descriptor']):v for n,r in meta.items() for v in r['structure']['methods']}; assert len(raw)==207
actual_filtered={(r['symbol'].split('#')[0],r['rawMetadata']['name'],r['rawMetadata']['descriptor']):r for r in filtered}
assert len(filtered)==len(actual_filtered)==101 and raw.keys()-expected.keys()-{k for k,v in raw.items() if not v['hasCode']}==actual_filtered.keys()
assert Counter(k[0].split('/')[-1] for k in actual_filtered)==Counter({**{n:len(v) for n,v in cfg['generatedMethods'].items()},**{n:3 for n in cfg['standardEnumSources']},**{n:1 for n in cfg['privateUtilitySources']}})
for key,r in actual_filtered.items():
 assert r['rawMetadata']==raw[key] and r['manualExclusion'] is False and r['artificialInvocation'] is False
 stem=key[0].split('/')[-1]
 if stem in cfg['privateUtilitySources']:assert key[1:]==('<init>','()V') and raw[key]['flags']==2 and raw[key]['codeLength']==5 and 'UTILITY' in r['status']
 elif stem in cfg['standardEnumSources']:assert key[1] in ['values','valueOf','$values'] and 'ENUM' in r['status']
 else:assert key[1] in cfg['generatedMethods'][stem] and 'RECORD' in r['status']
abstract=load(S/'abstract-contracts.json');noncode={k:v for k,v in raw.items() if v['hasCode'] is False};assert len(abstract)==len(noncode)==2 and {a['symbol'] for a in abstract}=={k[0]+'#'+k[1]+k[2] for k in noncode}
for a in abstract:assert a['status']=='ABSTRACT_INTERFACE_CONTRACT_NO_EXECUTABLE_CODE' and a['runtimeMethodCoverage'] is None and a['relatedCaseKeys']==[cases['ID' if '/ProtocolId#' in a['symbol'] else 'EG']['caseKey']]
assert Counter(c['path'] for c in classes)==Counter(r['sourcePath'] for r in inv)
total={k:dict(covered=0,missed=0) for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}
for n,artifact in meta.items():
 path=artifact['sourcePath']; p=R/path; text=p.read_text(); assert artifact['owner']==desc[path]['owner']==desc[path]['costOwner']==cfg['owner'] and sha(p)==artifact['sourceSha256']==desc[path]['sha256'] and artifact['classSha256']==ix[n]['sha256']
 c=next(c for c in classes if c['className']==n); assert c['sourceSha256']==sha(p) and c['classSha256']==ix[n]['sha256'] and c['crc64']==ix[n]['crc64'] and c['owner']==c['costOwner']==cfg['owner']
 if n.endswith('/package-info'):
  assert not artifact['structure']['methods'] and n not in xml and c['status']=='ANNOTATION_ONLY_NO_METHOD_NO_CLASS_COVERAGE_CREDIT';continue
 if not any(v['hasCode'] for v in artifact['structure']['methods']):
  assert n.endswith(('/ProtocolId','/WireEnum')) and not xml[n].findall('method') and c['status']=='DECLARATION_ONLY_NO_EXECUTABLE_METHOD_NO_COVERAGE_CREDIT';continue
 ct={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml[n].findall('counter')}; assert c['counters']==ct and all(v['missed']==0 for v in ct.values())
 for k in total:
  for v in ['covered','missed']:total[k][v]+=ct.get(k,{}).get(v,0)
 for key in sorted(k for k in expected if k[0]==n):
  r=got[key]; rule=cfg['methodRules'][n.split('/')[-1]][key[1]]; xm=expected[key]
  assert r['sourcePath']==path and r['sourceSha256']==sha(p) and r['owner']==r['costOwner']==cfg['owner'] and r['firstExecutableLine']==int(xm.get('line'))
  for a,b in [('relatedRd','relatedRd'),('ssSections','ssSections'),('contract','contract'),('staticPath','staticPath'),('caseLabels','cases')]:assert r[a]==rule[b]
  assert r['actualCaseKeys']==[cases[l]['caseKey'] for l in rule['cases']] and r['testIdAliases']==sorted({i for l in rule['cases'] for i in cases[l]['testIds']}) and r['perCaseProbeAttribution'] is None and r['allBranchOraclesIndividuallyVerified'] is False
  assert r['methodCountersFromSame120Run']=={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xm.findall('counter')}
  if p.stem=='IdValue':assert 'IdValue.validate(value);' in (R/next(p for p in scope if p.endswith('/UserId.java'))).read_text()
  if p.stem=='PathSyntax' and key[1]!='<clinit>':assert key[1] in (R/next(p for p in scope if p.endswith('/RelativePath.java'))).read_text()+(R/next(p for p in scope if p.endswith('/DisplayPath.java'))).read_text()
  if p.stem=='FixedWidthEncoder' and key[1]=='copy':assert text.count('copy(')>1
assert total==m['coverageReferences'] and {k:total[k]['covered'] for k in total}==dict(LINE=334,METHOD=104,CLASS=37,BRANCH=104,INSTRUCTION=1467)
task=next(r for r in load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks'] if r['id']==cfg['owner']);assert task['requirementIds']==['MSG-'+str(i).zfill(3) for i in range(1,12)] and set(cfg['sourcePaths'])<=set(task['ownedArtifacts'])
allowedRd=set(task['requirementIds'])|{'MQ-014','MQ-016','MQ-017','FIL-006'};assert all(set(rule['relatedRd'])<=allowedRd for rules in cfg['methodRules'].values() for rule in rules.values())
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
for k,v in [('sourceArtifacts',41),('physicalClasses',41),('codeClasses',37),('annotationOnly',2),('abstractMethods',2),('rawMethods',207),('officialMeasuredMethods',104),('standardGeneratedFilters',101),('existingActualCaseKeys',7)]:assert type(m[k]) is int and m[k]==v
assert all(m[k]==0 for k in ['productTestsExecuted','newProductTests','newJavaCompilerExecutions','sourceRegistryAcceptedDelta','newAcceptance']) and m['formalUpdated'] is False and m['effortRate'] is None
fieldProof=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG24662-field-three-method19-trace-independent-v1/manifest.json';assert sha(fieldProof)=='a8bd6f0efaae5b85a2824e65563a8603d905844ddeb5334008c6b98d221601e2';proof=load(fieldProof);assert proof['actualExit']==0 and proof['source']==cfg['source'] and proof['testSource']==cfg['testSource'] and proof['newAcceptance']==0
prodPath=R/proof['producerManifest']['path'];assert sha(prodPath)==proof['producerManifest']['sha256'];prod=load(prodPath)
for name,h in prod['files'].items():assert sha(prodPath.parent/name)==h
fieldRows=load(prodPath.parent/'method-trace.json');oldRows=[r for r in fieldRows if r['owner']==cfg['owner']];oldClasses=[r for r in load(prodPath.parent/'class-trace.json') if r['owner']==cfg['owner']];oldCases=load(prodPath.parent/'case-oracles.json');oldSources={r['sourcePath'] for r in oldRows};oldNames={r['symbol'].split('#')[0] for r in oldRows};assert len(oldSources)==2 and len(oldRows)==17 and not oldSources&scope and not oldNames&set(meta);assert len([r for r in fieldRows if r['owner']=='WBS-P002-04'])==2
normalized=[dict(r,className=r['symbol'].split('#')[0],method=r['symbol'].split('#')[1].split('(',1)[0],descriptor='('+r['symbol'].split('(',1)[1]) for r in oldRows];allRows=normalized+rows;allSources=oldSources|scope;allNames=oldNames|set(meta);allCaseKeys={c['caseKey'] for c in oldCases.values()}|{c['caseKey'] for c in cases.values()};assert len(allSources)==43 and allSources==set(task['ownedArtifacts']) and len(allNames)==43 and len(allRows)==121 and len(allCaseKeys)==17
fullXml={c.get('name'):c for c in E.parse(parent/'coverage.xml').getroot().findall('.//class') if c.get('name') in allNames};fullExpected={(n,m.get('name'),m.get('desc')) for n,c in fullXml.items() for m in c.findall('method')};assert {(r['className'],r['method'],r['descriptor']) for r in allRows}==fullExpected and len(fullExpected)==121
ownerInventory=[r for r in load(R/cfg['metadataInventory']['path']) if r['sourcePath'] in allSources];assert len(ownerInventory)==43 and sum(len(r['structure']['methods']) for r in ownerInventory)==225 and sum(not m['hasCode'] for r in ownerInventory for m in r['structure']['methods'])==2
for r in ownerInventory:assert r['owner']==cfg['owner'] and sha(R/r['sourcePath'])==r['sourceSha256']
fullCounters={k:dict(covered=0,missed=0) for k in total}
for x in fullXml.values():
 for k in fullCounters:
  c=x.find("counter[@type='"+k+"']")
  if c is not None:
   for v in ['covered','missed']:fullCounters[k][v]+=int(c.get(v))
assert fullCounters['METHOD']['covered']==121 and fullCounters['CLASS']['covered']==39 and fullCounters['BRANCH']['covered']==188 and all(v['missed']==0 for v in fullCounters.values())
natural=sum('BRANCH' not in c['counters'] for c in oldClasses+classes if 'counters' in c);assert natural==28
summary=dict(owner=cfg['owner'],sourceArtifacts=43,physicalClasses=43,officialMeasuredClasses=39,officialMeasuredMethods=121,rawMethods=225,standardGeneratedFilters=102,abstractMethods=2,annotationClasses=2,actualExistingCaseRefs=17,naturalZeroBranchSources=28,strictNonemptySourceFourCounterGateExit=1,scopeReferenceComplete=True,methodReferencesComplete=True,perCaseProbeAttribution=None,allBranchOraclesIndividuallyVerified=False,newAcceptance=0,newRuntimeCoverage=False,coverageReferences=fullCounters,fieldProof=dict(path=str(fieldProof.relative_to(R)),sha256=sha(fieldProof)),fieldOtherOwnerExcluded={'WBS-P002-04':{'sourceArtifacts':1,'methods':2}},currentProducer=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),sourcePaths=sorted(allSources),methodSymbols=sorted(r['symbol'] for r in allRows))
O.mkdir();(O/'p00201-all43-reference-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n'); out=dict(ownerScopeArtifacts=43,ownerPhysicalClasses=43,ownerMeasuredMethods=121,ownerExistingCaseRefs=17,ownerNaturalZeroBranchSources=28,ownerSummarySha256=sha(O/'p00201-all43-reference-summary.json'),actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],testSource=cfg['testSource'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),sourceArtifacts=41,physicalClasses=41,codeClasses=37,annotationOnly=2,declarationOnlyInterfaces=2,abstractMethods=2,rawMethods=207,officialMeasuredMethods=104,standardGeneratedFilters=101,existingActualCaseKeys=7,coverageReferences=total,metadataNegativeChecks=checks,exclusiveRdOwnershipUnchanged=True,perCaseProbeAttribution=None,methodRelationsBoundOnly=True,allBranchOraclesIndividuallyVerified=False,productTestsExecuted=0,newProductTests=0,newJavaCompilerExecutions=0,sourceRegistryAcceptedDelta=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,methods=104,filters=101,cases=7,metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
