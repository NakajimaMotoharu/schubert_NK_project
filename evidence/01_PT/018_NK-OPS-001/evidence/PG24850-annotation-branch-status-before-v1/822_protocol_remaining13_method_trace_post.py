"""Reverse XML-to-trace join for Remaining protocol references, not a Java execution or acceptance."""
from pathlib import Path
from collections import Counter
import copy, datetime, hashlib, json, subprocess, xml.etree.ElementTree as E

R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'; S=B/'evidence/PG24838-protocol-remain13-method56-trace-v1'; O=B/'evidence/PG24840-protocol-remain13-method56-trace-independent-v1'
assert not O.exists()
load=lambda p:json.loads(p.read_bytes()); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=S/'manifest.json'; assert sha(mp)=='feca88f8fc6a76a19fd3dc4a5a652a85979371971984b01a8fa5fee90f4cf8e9'
m=load(mp); cfg=load(R/m['config']['path']); assert sha(R/m['config']['path'])==m['config']['sha256']
for n,h in m['files'].items():assert sha(S/n)==h
for ref in [cfg['normalProof'],cfg['metadataInventory'],cfg['descriptorInventory'],cfg['physicalIndex'],*cfg['oracleDocuments']]:assert sha(R/ref['path'])==ref['sha256']
normal=load(R/cfg['normalProof']['path']); parent=(R/cfg['normalProof']['path']).parent
assert normal['actualExit']==0 and normal['source']==cfg['testSource'] and normal['productionCoreMain']==cfg['source'] and normal['tests']==120
for n in ['coverage.xml','testcases.safe.xml']:assert sha(parent/n)==normal['files'][n]
scope=set(cfg['sourcePaths']); inv=[r for r in load(R/cfg['metadataInventory']['path']) if r['sourcePath'] in scope]; assert len(inv)==14
meta={r['physicalKey'].split(':',1)[1].removesuffix('.class'):r for r in inv}; ix=load(R/cfg['physicalIndex']['path']); desc={r['path']:r for r in load(R/cfg['descriptorInventory']['path']) if r['path'] in scope}
xml={r.get('name'):r for r in E.parse(parent/'coverage.xml').getroot().findall('.//class') if r.get('name') in meta}
expected={(n,x.get('name'),x.get('desc')):x for n,c in xml.items() for x in c.findall('method')}
rows=load(S/'method-trace.json'); cases=load(S/'case-oracles.json'); classes=load(S/'class-trace.json'); filtered=load(S/'standard-filter.json'); got={(r['className'],r['method'],r['descriptor']):r for r in rows}
assert len(rows)==len(got)==len(expected)==56 and got.keys()==expected.keys() and len(cases)==28
actual={r.get('classname')+'#'+r.get('name') for r in E.parse(parent/'testcases.safe.xml').getroot().findall('testcase')}; assert len(actual)==120
for label,c in cases.items():
 original=cfg['cases'][label]; assert c['caseKey']==original['caseKey'] and c['caseKey'] in actual and c['testIds']==original['testIds'] and c['independentOracle']==original['independentOracle'] and c['individualProbeAttribution'] is None
 p=R/c['path']; lines=p.read_text().splitlines(keepends=True); body=''.join(lines[c['declarationLine']-1:c['bodyEndLine']]); assert sha(p)==c['sourceSha256'] and hashlib.sha256(body.encode()).hexdigest()==c['assertionBodySha256'] and 'assert' in body
 assert hashlib.sha256(subprocess.check_output(['git','show',cfg['testSource']+':'+c['path']])).hexdigest()==sha(p)
raw={(n,v['name'],v['descriptor']):v for n,r in meta.items() for v in r['structure']['methods']}; assert len(raw)==76
actual_filtered={(r['symbol'].split('#')[0],r['rawMetadata']['name'],r['rawMetadata']['descriptor']):r for r in filtered}
assert len(filtered)==len(actual_filtered)==20 and raw.keys()-expected.keys()==actual_filtered.keys()
assert Counter(k[0].split('/')[-1] for k in actual_filtered)==Counter({'LargeResultContent':6,'LargeResultRecordCodec':1,'MediaDescriptorValidator':1,'JstWireTimestamp':1,'ContentDisposition':3,'MediaType':4,'BrokerTopology':3,'MediaDescriptorValidator$1':1})
filterProof=load(R/cfg['standardFilterProof']['path']);assert sha(R/cfg['standardFilterProof']['path'])==cfg['standardFilterProof']['sha256'] and filterProof['actualExit']==0 and filterProof['officialFilterApplied'] is True
compilerProof={r['name']:r for r in filterProof['compilerRows']}
for key,r in actual_filtered.items():
 assert r['rawMetadata']==raw[key] and r['manualExclusion'] is False and r['artificialInvocation'] is False
 if key[0] in cfg['standardSwitchClasses']:
  proof=compilerProof[key[0]];assert proof['sha256']==meta[key[0]]['classSha256']==ix[key[0]]['sha256'] and proof['crc64']==ix[key[0]]['crc64'] and proof['syntheticSwitchMap'] is True and type(proof['officialMeasuredMethods']) is int and proof['officialMeasuredMethods']==0 and proof['manualExclusion'] is False and key[1:]==('<clinit>','()V') and not xml[key[0]].findall('method')
 else:
  stem=key[0].split('/')[-1];text=(R/meta[key[0]]['sourcePath']).read_text()
  if stem in cfg['privateUtilitySources']:assert key[1:]==('<init>','()V') and raw[key]['flags']==2 and raw[key]['codeLength']==5 and ('private '+stem+'() {}') in text
  elif stem in cfg['standardEnumSources']:assert key[1] in ['values','valueOf','$values','<init>'] and ('public enum '+stem) in text
  else:assert key[1] in cfg['generatedMethods'][stem] and ('public record '+stem+'(') in text
assert Counter(c['path'] for c in classes)==Counter({path:sum(v['sourcePath']==path for v in meta.values()) for path in scope})
total={k:dict(covered=0,missed=0) for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}
for n,artifact in meta.items():
 path=artifact['sourcePath']; owner=cfg['ownersBySource'][path]; p=R/path; text=p.read_text(); assert artifact['owner']==desc[path]['owner']==desc[path]['costOwner']==owner and sha(p)==artifact['sourceSha256']==desc[path]['sha256'] and artifact['classSha256']==ix[n]['sha256']
 c=next(c for c in classes if c['className']==n); assert c['sourceSha256']==sha(p) and c['classSha256']==ix[n]['sha256'] and c['crc64']==ix[n]['crc64'] and c['owner']==c['costOwner']==owner
 if n.endswith('/package-info'):
  assert not artifact['structure']['methods'] and n not in xml and c['status']=='ANNOTATION_ONLY_NO_METHOD_NO_CLASS_COVERAGE_CREDIT';continue
 ct={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml[n].findall('counter')}; assert c['counters']==ct and all(v['missed']==0 for v in ct.values())
 for k in total:
  for v in ['covered','missed']:total[k][v]+=ct.get(k,{}).get(v,0)
 for key in sorted(k for k in expected if k[0]==n):
  r=got[key]; rules=cfg['methodRules'][p.stem];ruleKey=key[1]+'#'+key[2] if key[1]+'#'+key[2] in rules else key[1];rule=rules[ruleKey]; xm=expected[key]
  assert r['sourcePath']==path and r['sourceSha256']==sha(p) and r['owner']==r['costOwner']==owner and r['firstExecutableLine']==int(xm.get('line'))
  for a,b in [('relatedRd','relatedRd'),('ssSections','ssSections'),('contract','contract'),('staticPath','staticPath'),('caseLabels','cases')]:assert r[a]==rule[b]
  assert r['actualCaseKeys']==[cases[l]['caseKey'] for l in rule['cases']] and r['testIdAliases']==sorted({i for l in rule['cases'] for i in cases[l]['testIds']}) and r['perCaseProbeAttribution'] is None and r['allBranchOraclesIndividuallyVerified'] is False
  assert r['methodCountersFromSame120Run']=={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xm.findall('counter')}
  assert r['ui']==cfg['referencesByOwner'][owner]['ui'] and r['ss']==cfg['referencesByOwner'][owner]['ss']
  if p.stem=='LargeResultRecordCodec' and key[1] in ['readExact','sha256Digest','digestFor']:assert text.count(key[1]+'(')>1
  if p.stem=='MediaDescriptorValidator' and key[1] not in ['<clinit>','validate']:assert text.count(key[1]+'(')>1
  if p.stem=='ContentDisposition':assert r['caseLabels']==['MD']
  if p.stem=='BrokerTopology':assert r['caseLabels']==(['BP','BN'] if key[1]=='requireAddress' else ['BP'])
  if p.stem=='FailedJmsIsolationException':assert r['caseLabels']==['I9','I10','I11','I12']
  if p.stem=='UnconfirmedJmsRollbackException':assert r['caseLabels']==['U5','U6','U7','U8']
assert total==m['coverageReferences'] and {k:total[k]['covered'] for k in total}==dict(LINE=262,METHOD=56,CLASS=12,BRANCH=147,INSTRUCTION=1138)
# No exclusive RD ownership is assigned to P00102; MQ references remain shared.
tasks={r['id']:r for r in load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks']};registered={r['path']:r for r in load(R/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json')['artifacts']};baseline=[];added=[]
for path,owner in cfg['ownersBySource'].items():
 if path in tasks[owner]['ownedArtifacts']:baseline.append(path)
 else:
  row=cfg['postBaselineExplicitOwners'][path];assert registered[path]==row and row['owner']==row['costOwner']==owner and row['sha256']==sha(R/path) and row['acceptance']=='UNASSESSED' and 'explicit per-source' in row['basis'];added.append(path)
assert len(baseline)==11 and len(added)==2
sample=rows[0]
def row_contract(r):
 key=(r['className'],r['method'],r['descriptor']); reference=got[key]
 assert type(r['firstExecutableLine']) is int and r['firstExecutableLine']==reference['firstExecutableLine'] and r['owner']==r['costOwner']==cfg['ownersBySource'][r['sourcePath']]==reference['owner'] and r['sourceSha256']==reference['sourceSha256'] and r['actualCaseKeys']==reference['actualCaseKeys'] and r['perCaseProbeAttribution'] is None and r['methodCountersFromSame120Run']==reference['methodCountersFromSame120Run']
checks=0
wrongOwner='WBS-P002-01' if sample['owner']!='WBS-P002-01' else 'WBS-P002-03'
for field,value in [('descriptor','()Z'),('owner',wrongOwner),('actualCaseKeys',['unknown#case()']),('sourceSha256','0'*64),('perCaseProbeAttribution',False),('firstExecutableLine',True),('methodCountersFromSame120Run',{})]:
 bad=copy.deepcopy(sample);bad[field]=value;assert json.dumps(bad,sort_keys=True)!=json.dumps(sample,sort_keys=True)
 try:row_contract(bad)
 except (AssertionError,KeyError):checks+=1
 else:raise AssertionError('false Layout reference accepted')
for k,v in [('sourceArtifacts',13),('codeClasses',12),('annotationOnly',1),('rawMethods',76),('officialMeasuredMethods',56),('standardGeneratedFilters',20),('existingActualCaseKeys',28)]:assert type(m[k]) is int and m[k]==v
assert all(m[k]==0 for k in ['productTestsExecuted','newProductTests','newJavaCompilerExecutions','sourceRegistryAcceptedDelta','newAcceptance']) and m['formalUpdated'] is False and m['effortRate'] is None
assert sha(R/'evidence/01_PT/018_NK-OPS-001/input/821_protocol_remaining13_method_trace.py')==m['toolSha256']
assert sum(c['branchStatus']=='STANDARD_COMPILER_FILTERED_NOT_NATURAL_SOURCE_ZERO' for c in classes)==1
assert sum(c.get('branchStatus')=='NATURAL_ZERO_NA_NOT_100' for c in classes)==3
O.mkdir(); out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],testSource=cfg['testSource'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),sourceArtifacts=13,physicalClasses=14,codeClasses=12,annotationOnly=1,rawMethods=76,officialMeasuredMethods=56,standardGeneratedFilters=20,existingActualCaseKeys=28,coverageReferences=total,metadataNegativeChecks=checks,exclusiveRdOwnershipUnchanged=True,naturalZeroBranchSources=3,compilerFilteredClasses=1,baselineSourceArtifacts=11,postBaselineExplicitSourceArtifacts=2,postBaselineUnaccepted=True,ownersBySource=cfg['ownersBySource'],filterProof=cfg['standardFilterProof'],perCaseProbeAttribution=None,methodRelationsBoundOnly=True,allBranchOraclesIndividuallyVerified=False,productTestsExecuted=0,newProductTests=0,newJavaCompilerExecutions=0,sourceRegistryAcceptedDelta=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,methods=len(rows),filters=len(filtered),cases=len(cases),metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
