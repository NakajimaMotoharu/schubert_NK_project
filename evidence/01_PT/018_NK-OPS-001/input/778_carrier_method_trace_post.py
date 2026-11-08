"""Reverse XML-to-trace join for Immutable carrier references, not a Java execution or acceptance."""
from pathlib import Path
from collections import Counter
import copy, datetime, hashlib, json, subprocess, xml.etree.ElementTree as E

R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'; S=B/'evidence/PG24716-carrier-method14-trace-v1'; O=B/'evidence/PG24718-carrier-method14-trace-independent-v1'
assert not O.exists()
load=lambda p:json.loads(p.read_bytes()); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=S/'manifest.json'; assert sha(mp)=='600d2262dbcd725e611c7d0874a5b5108da2791d2600f40be3e96059de10adad'
m=load(mp); cfg=load(R/m['config']['path']); assert sha(R/m['config']['path'])==m['config']['sha256']
for n,h in m['files'].items():assert sha(S/n)==h
for ref in [cfg['normalProof'],cfg['metadataInventory'],cfg['descriptorInventory'],cfg['physicalIndex'],*cfg['oracleDocuments']]:assert sha(R/ref['path'])==ref['sha256']
normal=load(R/cfg['normalProof']['path']); parent=(R/cfg['normalProof']['path']).parent
assert normal['actualExit']==0 and normal['source']==cfg['testSource'] and normal['productionCoreMain']==cfg['source'] and normal['tests']==120
for n in ['coverage.xml','testcases.safe.xml']:assert sha(parent/n)==normal['files'][n]
scope=set(cfg['sourcePaths']); inv=[r for r in load(R/cfg['metadataInventory']['path']) if r['sourcePath'] in scope]; assert len(inv)==11
meta={r['physicalKey'].split(':',1)[1].removesuffix('.class'):r for r in inv}; ix=load(R/cfg['physicalIndex']['path']); desc={r['path']:r for r in load(R/cfg['descriptorInventory']['path']) if r['path'] in scope}
xml={r.get('name'):r for r in E.parse(parent/'coverage.xml').getroot().findall('.//class') if r.get('name') in meta}
expected={(n,x.get('name'),x.get('desc')):x for n,c in xml.items() for x in c.findall('method')}
rows=load(S/'method-trace.json'); cases=load(S/'case-oracles.json'); classes=load(S/'class-trace.json'); filtered=load(S/'standard-filter.json'); got={(r['className'],r['method'],r['descriptor']):r for r in rows}
assert len(rows)==len(got)==len(expected)==14 and got.keys()==expected.keys() and len(cases)==2
actual={r.get('classname')+'#'+r.get('name') for r in E.parse(parent/'testcases.safe.xml').getroot().findall('testcase')}; assert len(actual)==120
for label,c in cases.items():
 original=cfg['cases'][label]; assert c['caseKey']==original['caseKey'] and c['caseKey'] in actual and c['testIds']==original['testIds'] and c['independentOracle']==original['independentOracle'] and c['individualProbeAttribution'] is None
 p=R/c['path']; lines=p.read_text().splitlines(keepends=True); body=''.join(lines[c['declarationLine']-1:c['bodyEndLine']]); assert sha(p)==c['sourceSha256'] and hashlib.sha256(body.encode()).hexdigest()==c['assertionBodySha256'] and 'assert' in body
 assert hashlib.sha256(subprocess.check_output(['git','show',cfg['testSource']+':'+c['path']])).hexdigest()==sha(p)
raw={(n,v['name'],v['descriptor']):v for n,r in meta.items() for v in r['structure']['methods']}; assert len(raw)==39
actual_filtered={(r['symbol'].split('#')[0],r['rawMetadata']['name'],r['rawMetadata']['descriptor']):r for r in filtered}
assert len(filtered)==len(actual_filtered)==20 and raw.keys()-expected.keys()-{k for k,v in raw.items() if not v['hasCode']}==actual_filtered.keys()
assert Counter(k[0].split('/')[-1] for k in actual_filtered)==Counter({'FieldValue$Flag':4,'FieldValue$Numeric':4,'FieldValue$Text':3,'FieldValue$Unset':4,'WireMessage':5})
for key,r in actual_filtered.items():
 assert r['rawMetadata']==raw[key] and r['manualExclusion'] is False and r['artificialInvocation'] is False
 stem=key[0].split('/')[-1]
 if stem in cfg['standardEnumSymbols']:assert key[1] in ['values','valueOf','$values','<init>'] and 'ENUM' in r['status']
 else:assert key[1] in cfg['generatedMethods'][stem] and 'RECORD' in r['status']
abstract=load(S/'abstract-contracts.json');noncode={k:v for k,v in raw.items() if v['hasCode'] is False};assert len(abstract)==len(noncode)==5 and {a['symbol'] for a in abstract}=={k[0]+'#'+k[1]+k[2] for k in noncode}
for a in abstract:assert a['status']=='ABSTRACT_INTERFACE_CONTRACT_NO_EXECUTABLE_CODE' and a['runtimeMethodCoverage'] is None and a['relatedCaseKeys']==[cases['W1']['caseKey']]
assert Counter(c['path'] for c in classes)==Counter(r['sourcePath'] for r in inv)
total={k:dict(covered=0,missed=0) for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}
for n,artifact in meta.items():
 path=artifact['sourcePath']; p=R/path; text=p.read_text(); assert artifact['owner']==desc[path]['owner']==desc[path]['costOwner']==cfg['owner'] and sha(p)==artifact['sourceSha256']==desc[path]['sha256'] and artifact['classSha256']==ix[n]['sha256']
 c=next(c for c in classes if c['className']==n); assert c['sourceSha256']==sha(p) and c['classSha256']==ix[n]['sha256'] and c['crc64']==ix[n]['crc64'] and c['owner']==c['costOwner']==cfg['owner']
 if n.endswith('/package-info'):
  assert not artifact['structure']['methods'] and n not in xml and c['status']=='ANNOTATION_ONLY_NO_METHOD_NO_CLASS_COVERAGE_CREDIT';continue
 if not any(v['hasCode'] for v in artifact['structure']['methods']):
  assert n.endswith(('/FieldValue','/LayoutPayload')) and not xml[n].findall('method') and c['status']=='DECLARATION_ONLY_NO_EXECUTABLE_METHOD_NO_COVERAGE_CREDIT';continue
 ct={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml[n].findall('counter')}; assert c['counters']==ct and all(v['missed']==0 for v in ct.values())
 for k in total:
  for v in ['covered','missed']:total[k][v]+=ct.get(k,{}).get(v,0)
 for key in sorted(k for k in expected if k[0]==n):
  r=got[key]; rule=cfg['methodRules'][n.split('/')[-1]][key[1]]; xm=expected[key]
  assert r['sourcePath']==path and r['sourceSha256']==sha(p) and r['owner']==r['costOwner']==cfg['owner'] and r['firstExecutableLine']==int(xm.get('line'))
  for a,b in [('relatedRd','relatedRd'),('ssSections','ssSections'),('contract','contract'),('staticPath','staticPath'),('caseLabels','cases')]:assert r[a]==rule[b]
  assert r['actualCaseKeys']==[cases[l]['caseKey'] for l in rule['cases']] and r['testIdAliases']==sorted({i for l in rule['cases'] for i in cases[l]['testIds']}) and r['perCaseProbeAttribution'] is None and r['allBranchOraclesIndividuallyVerified'] is False
  assert r['methodCountersFromSame120Run']=={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xm.findall('counter')}
  if p.stem=='FieldValueSet' and key[1]=='empty':assert 'return new FieldValueSet(Map.of());' in text
  if p.stem=='WireMessage':assert 'header.dataLength() != payload.dataLength()' in text and 'header.recordLength() != payload.recordLength()' in text and 'header.recordCount() != payload.recordCount()' in text
# BUG2551: all four observed record declarations, including the generic wire carrier.
field=(R/next(p for p in scope if p.endswith('/FieldValue.java'))).read_text();wire=(R/next(p for p in scope if p.endswith('/WireMessage.java'))).read_text();assert all(('record '+name+'(') in field for name in ['Text','Numeric','Flag']) and 'record WireMessage<P extends LayoutPayload>(' in wire
assert total==m['coverageReferences'] and {k:total[k]['covered'] for k in total}==dict(LINE=36,METHOD=14,CLASS=6,BRANCH=16,INSTRUCTION=180)
# No exclusive RD ownership is assigned to P00102; MQ references remain shared.
task=next(r for r in load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks'] if r['id']==cfg['owner']); assert task['requirementIds']==[] and set(cfg['sourcePaths'])<=set(task['ownedArtifacts'])
assert all(set(rule['relatedRd'])<=set(['MQ-017','MQ-018']) for rules in cfg['methodRules'].values() for rule in rules.values())
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
for k,v in [('sourceArtifacts',7),('physicalClasses',11),('codeClasses',6),('annotationOnly',3),('abstractMethods',5),('rawMethods',39),('officialMeasuredMethods',14),('standardGeneratedFilters',20),('existingActualCaseKeys',2)]:assert type(m[k]) is int and m[k]==v
assert all(m[k]==0 for k in ['productTestsExecuted','newProductTests','newJavaCompilerExecutions','sourceRegistryAcceptedDelta','newAcceptance']) and m['formalUpdated'] is False and m['effortRate'] is None
O.mkdir(); out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],testSource=cfg['testSource'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),sourceArtifacts=7,physicalClasses=11,codeClasses=6,annotationOnly=3,declarationOnlyInterfaces=2,abstractMethods=5,rawMethods=39,officialMeasuredMethods=14,standardGeneratedFilters=20,existingActualCaseKeys=2,coverageReferences=total,metadataNegativeChecks=checks,exclusiveRdOwnershipUnchanged=True,recordDeclarationFormsVerified=4,perCaseProbeAttribution=None,methodRelationsBoundOnly=True,allBranchOraclesIndividuallyVerified=False,productTestsExecuted=0,newProductTests=0,newJavaCompilerExecutions=0,sourceRegistryAcceptedDelta=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,methods=14,filters=20,cases=2,metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
