"""Reverse XML-to-trace join for Field catalog references, not a Java execution or acceptance."""
from pathlib import Path
from collections import Counter
import copy, datetime, hashlib, json, subprocess, xml.etree.ElementTree as E

R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'; S=B/'evidence/PG24704-catalog-method33-trace-v1'; O=B/'evidence/PG24706-catalog-method33-trace-independent-v1'
assert not O.exists()
load=lambda p:json.loads(p.read_bytes()); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=S/'manifest.json'; assert sha(mp)=='bb25c1f48ea1588d6742c75ecf9ffa94bf3d31ffa0a017efa576a1f10e2df770'
m=load(mp); cfg=load(R/m['config']['path']); assert sha(R/m['config']['path'])==m['config']['sha256']
for n,h in m['files'].items():assert sha(S/n)==h
for ref in [cfg['normalProof'],cfg['metadataInventory'],cfg['descriptorInventory'],cfg['physicalIndex'],*cfg['oracleDocuments']]:assert sha(R/ref['path'])==ref['sha256']
normal=load(R/cfg['normalProof']['path']); parent=(R/cfg['normalProof']['path']).parent
assert normal['actualExit']==0 and normal['source']==cfg['testSource'] and normal['productionCoreMain']==cfg['source'] and normal['tests']==120
for n in ['coverage.xml','testcases.safe.xml']:assert sha(parent/n)==normal['files'][n]
scope=set(cfg['sourcePaths']); inv=[r for r in load(R/cfg['metadataInventory']['path']) if r['sourcePath'] in scope]; assert len(inv)==10
meta={r['physicalKey'].split(':',1)[1].removesuffix('.class'):r for r in inv}; ix=load(R/cfg['physicalIndex']['path']); desc={r['path']:r for r in load(R/cfg['descriptorInventory']['path']) if r['path'] in scope}
xml={r.get('name'):r for r in E.parse(parent/'coverage.xml').getroot().findall('.//class') if r.get('name') in meta}
expected={(n,x.get('name'),x.get('desc')):x for n,c in xml.items() for x in c.findall('method')}
rows=load(S/'method-trace.json'); cases=load(S/'case-oracles.json'); classes=load(S/'class-trace.json'); filtered=load(S/'standard-filter.json'); got={(r['className'],r['method'],r['descriptor']):r for r in rows}
assert len(rows)==len(got)==len(expected)==33 and got.keys()==expected.keys() and len(cases)==4
actual={r.get('classname')+'#'+r.get('name') for r in E.parse(parent/'testcases.safe.xml').getroot().findall('testcase')}; assert len(actual)==120
for label,c in cases.items():
 original=cfg['cases'][label]; assert c['caseKey']==original['caseKey'] and c['caseKey'] in actual and c['testIds']==original['testIds'] and c['independentOracle']==original['independentOracle'] and c['individualProbeAttribution'] is None
 p=R/c['path']; lines=p.read_text().splitlines(keepends=True); body=''.join(lines[c['declarationLine']-1:c['bodyEndLine']]); assert sha(p)==c['sourceSha256'] and hashlib.sha256(body.encode()).hexdigest()==c['assertionBodySha256'] and 'assert' in body
 assert hashlib.sha256(subprocess.check_output(['git','show',cfg['testSource']+':'+c['path']])).hexdigest()==sha(p)
raw={(n,v['name'],v['descriptor']):v for n,r in meta.items() for v in r['structure']['methods']}; assert len(raw)==70
actual_filtered={(r['symbol'].split('#')[0],r['rawMetadata']['name'],r['rawMetadata']['descriptor']):r for r in filtered}
assert len(filtered)==len(actual_filtered)==37 and raw.keys()-expected.keys()==actual_filtered.keys()
assert Counter(k[0].split('/')[-1] for k in actual_filtered)==Counter({'FieldDefinition':13,'LayoutFields':6,'FieldArea':4,'WireType':4,'Presence':4,'Padding':4,'FieldDefinition$1':1,'LayoutFieldCatalog$1':1})
for key,r in actual_filtered.items():
 assert r['rawMetadata']==raw[key] and r['manualExclusion'] is False and r['artificialInvocation'] is False
 stem=key[0].split('/')[-1]
 if key[0] in cfg['standardSwitchClasses']:
  proofPath=R/cfg['standardFilterProof']['path'];assert sha(proofPath)==cfg['standardFilterProof']['sha256'];proof=next(x for x in load(proofPath)['compilerRows'] if x['name']==key[0]);assert key[1:]==('<clinit>','()V') and proof['sha256']==meta[key[0]]['classSha256']==ix[key[0]]['sha256'] and proof['crc64']==ix[key[0]]['crc64'] and proof['syntheticSwitchMap'] is True and 'SWITCHMAP' in r['status']
 elif stem in cfg['standardEnumSources']:assert key[1] in ['values','valueOf','$values','<init>'] and 'ENUM' in r['status']
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
  if p.stem=='FieldDefinition' and key[1]=='checkedEnd':assert text.count('checkedEnd(')==3
  if p.stem=='LayoutFields' and key[1]=='validateArea':assert text.count('validateArea(')==3
  if p.stem=='LayoutFieldCatalog' and '$' not in n and key[1] in ['appendRows','parseArea','parseWireType','parsePresence','paddingFor','validateFixedField','javaTypeFor','wireCode','presenceCode','parsePositiveInt']:assert text.count(key[1]+'(')>1
assert total==m['coverageReferences'] and {k:total[k]['covered'] for k in total}==dict(LINE=184,METHOD=33,CLASS=8,BRANCH=76,INSTRUCTION=853)
# No exclusive RD ownership is assigned to P00102; MQ references remain shared.
task=next(r for r in load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks'] if r['id']==cfg['owner']); assert task['requirementIds']==[] and set(cfg['sourcePaths'])<=set(task['ownedArtifacts'])
assert all(set(rule['relatedRd'])<=set(['MQ-017']) for rules in cfg['methodRules'].values() for rule in rules.values())
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
for k,v in [('sourceArtifacts',7),('physicalClasses',10),('codeClasses',8),('annotationOnly',0),('rawMethods',70),('officialMeasuredMethods',33),('standardGeneratedFilters',37),('existingActualCaseKeys',4)]:assert type(m[k]) is int and m[k]==v
assert all(m[k]==0 for k in ['productTestsExecuted','newProductTests','newJavaCompilerExecutions','sourceRegistryAcceptedDelta','newAcceptance']) and m['formalUpdated'] is False and m['effortRate'] is None
O.mkdir(); out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],testSource=cfg['testSource'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),sourceArtifacts=7,physicalClasses=10,codeClasses=8,standardCompilerClasses=2,annotationOnly=0,rawMethods=70,officialMeasuredMethods=33,standardGeneratedFilters=37,existingActualCaseKeys=4,coverageReferences=total,metadataNegativeChecks=checks,exclusiveRdOwnershipUnchanged=True,standardCompilerClassBranchStatusOverrides={name:'STANDARD_COMPILER_FILTER_NOT_NATURAL_SOURCE_ZERO' for name in cfg['standardSwitchClasses']},perCaseProbeAttribution=None,methodRelationsBoundOnly=True,allBranchOraclesIndividuallyVerified=False,productTestsExecuted=0,newProductTests=0,newJavaCompilerExecutions=0,sourceRegistryAcceptedDelta=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,methods=33,filters=37,cases=4,metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
