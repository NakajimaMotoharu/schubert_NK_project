"""Reverse XML-to-trace join for Header codec references, not a Java execution or acceptance."""
from pathlib import Path
from collections import Counter
import copy, datetime, hashlib, json, subprocess, xml.etree.ElementTree as E

R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'; S=B/'evidence/PG24806-headercodec5-method14-trace-v1'; O=B/'evidence/PG24808-headercodec5-method14-trace-independent-v1'
assert not O.exists()
load=lambda p:json.loads(p.read_bytes()); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=S/'manifest.json'; assert sha(mp)=='18cbc1aecbd1bcb5bbd841a6e6d06726a3b6620fb4c1cc2d30944b9b71331263'
m=load(mp); cfg=load(R/m['config']['path']); assert sha(R/m['config']['path'])==m['config']['sha256']
for n,h in m['files'].items():assert sha(S/n)==h
for ref in [cfg['normalProof'],cfg['metadataInventory'],cfg['descriptorInventory'],cfg['physicalIndex'],*cfg['oracleDocuments']]:assert sha(R/ref['path'])==ref['sha256']
normal=load(R/cfg['normalProof']['path']); parent=(R/cfg['normalProof']['path']).parent
assert normal['actualExit']==0 and normal['source']==cfg['testSource'] and normal['productionCoreMain']==cfg['source'] and normal['tests']==120
for n in ['coverage.xml','testcases.safe.xml']:assert sha(parent/n)==normal['files'][n]
scope=set(cfg['sourcePaths']); inv=[r for r in load(R/cfg['metadataInventory']['path']) if r['sourcePath'] in scope]; assert len(inv)==5
meta={r['physicalKey'].split(':',1)[1].removesuffix('.class'):r for r in inv}; ix=load(R/cfg['physicalIndex']['path']); desc={r['path']:r for r in load(R/cfg['descriptorInventory']['path']) if r['path'] in scope}
xml={r.get('name'):r for r in E.parse(parent/'coverage.xml').getroot().findall('.//class') if r.get('name') in meta}
expected={(n,x.get('name'),x.get('desc')):x for n,c in xml.items() for x in c.findall('method')}
rows=load(S/'method-trace.json'); cases=load(S/'case-oracles.json'); classes=load(S/'class-trace.json'); filtered=load(S/'standard-filter.json'); got={(r['className'],r['method'],r['descriptor']):r for r in rows}
assert len(rows)==len(got)==len(expected)==14 and got.keys()==expected.keys() and len(cases)==7
actual={r.get('classname')+'#'+r.get('name') for r in E.parse(parent/'testcases.safe.xml').getroot().findall('testcase')}; assert len(actual)==120
for label,c in cases.items():
 original=cfg['cases'][label]; assert c['caseKey']==original['caseKey'] and c['caseKey'] in actual and c['testIds']==original['testIds'] and c['independentOracle']==original['independentOracle'] and c['individualProbeAttribution'] is None
 p=R/c['path']; lines=p.read_text().splitlines(keepends=True); body=''.join(lines[c['declarationLine']-1:c['bodyEndLine']]); assert sha(p)==c['sourceSha256'] and hashlib.sha256(body.encode()).hexdigest()==c['assertionBodySha256'] and 'assert' in body
 assert hashlib.sha256(subprocess.check_output(['git','show',cfg['testSource']+':'+c['path']])).hexdigest()==sha(p)
raw={(n,v['name'],v['descriptor']):v for n,r in meta.items() for v in r['structure']['methods']}; assert len(raw)==40
actual_filtered={(r['symbol'].split('#')[0],r['rawMetadata']['name'],r['rawMetadata']['descriptor']):r for r in filtered}
assert len(filtered)==len(actual_filtered)==26 and raw.keys()-expected.keys()==actual_filtered.keys()
assert Counter(k[0].split('/')[-1] for k in actual_filtered)==Counter({'ExpectedRoute':8,'TransportMetadata':14,'TransportBodyType':4})
for key,r in actual_filtered.items():
 assert r['rawMetadata']==raw[key] and r['manualExclusion'] is False and r['artificialInvocation'] is False
 stem=key[0].split('/')[-1]
 if stem=='TransportBodyType':assert key[1] in ['values','valueOf','$values','<init>'] and 'ENUM' in r['status']
 else:assert key[1] in cfg['generatedMethods'][stem] and 'RECORD' in r['status']
assert Counter(c['path'] for c in classes)==Counter({p:1 for p in scope})
total={k:dict(covered=0,missed=0) for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}
for n,artifact in meta.items():
 path=artifact['sourcePath']; p=R/path; text=p.read_text(); assert artifact['owner']==desc[path]['owner']==desc[path]['costOwner']==cfg['owner'] and sha(p)==artifact['sourceSha256']==desc[path]['sha256'] and artifact['classSha256']==ix[n]['sha256']
 c=next(c for c in classes if c['path']==path); assert c['sourceSha256']==sha(p) and c['classSha256']==ix[n]['sha256'] and c['crc64']==ix[n]['crc64'] and c['owner']==c['costOwner']==cfg['owner']
 if n.endswith('/package-info'):
  assert not artifact['structure']['methods'] and n not in xml and c['status']=='ANNOTATION_ONLY_NO_METHOD_NO_CLASS_COVERAGE_CREDIT';continue
 ct={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml[n].findall('counter')}; assert c['counters']==ct and all(v['missed']==0 for v in ct.values())
 for k in total:
  for v in ['covered','missed']:total[k][v]+=ct.get(k,{}).get(v,0)
 for key in sorted(k for k in expected if k[0]==n):
  r=got[key]; rules=cfg['methodRules'][p.stem];ruleKey=key[1]+'#'+key[2] if key[1]+'#'+key[2] in rules else key[1];rule=rules[ruleKey]; xm=expected[key]
  assert r['sourcePath']==path and r['sourceSha256']==sha(p) and r['owner']==r['costOwner']==cfg['owner'] and r['firstExecutableLine']==int(xm.get('line'))
  for a,b in [('relatedRd','relatedRd'),('ssSections','ssSections'),('contract','contract'),('staticPath','staticPath'),('caseLabels','cases')]:assert r[a]==rule[b]
  assert r['actualCaseKeys']==[cases[l]['caseKey'] for l in rule['cases']] and r['testIdAliases']==sorted({i for l in rule['cases'] for i in cases[l]['testIds']}) and r['perCaseProbeAttribution'] is None and r['allBranchOraclesIndividuallyVerified'] is False
  assert r['methodCountersFromSame120Run']=={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xm.findall('counter')}
  if p.stem=='HeaderCodec' and key[1] in ['put','slice','numericInt','requiredText','canonicalUuid']:assert text.count(key[1]+'(')>1
  if p.stem=='MessageEncodingException' and key[2]=='(Ljava/lang/String;)V':assert r['caseLabels']==['PE'] and 'new MessageEncodingException(' in (R/'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/codec/PayloadCodec.java').read_text()
assert total==m['coverageReferences'] and {k:total[k]['covered'] for k in total}==dict(LINE=113,METHOD=14,CLASS=5,BRANCH=36,INSTRUCTION=644)
# No exclusive RD ownership is assigned to P00102; MQ references remain shared.
task=next(r for r in load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks'] if r['id']==cfg['owner']); assert task['requirementIds']==[] and set(cfg['sourcePaths'])<=set(task['ownedArtifacts'])
assert all(set(rule['relatedRd'])<=set(['MSG-001','MSG-002','MSG-007','MSG-010','MQ-014','MQ-017']) for rules in cfg['methodRules'].values() for rule in rules.values())
sample=rows[0]
def row_contract(r):
 key=(r['className'],r['method'],r['descriptor']); reference=got[key]
 assert type(r['firstExecutableLine']) is int and r['firstExecutableLine']==reference['firstExecutableLine'] and r['owner']==r['costOwner']==cfg['owner'] and r['sourceSha256']==reference['sourceSha256'] and r['actualCaseKeys']==reference['actualCaseKeys'] and r['perCaseProbeAttribution'] is None and r['methodCountersFromSame120Run']==reference['methodCountersFromSame120Run']
checks=0
wrongOwner='WBS-P002-01' if sample['owner']!='WBS-P002-01' else 'WBS-P002-03'
for field,value in [('descriptor','()Z'),('owner',wrongOwner),('actualCaseKeys',['unknown#case()']),('sourceSha256','0'*64),('perCaseProbeAttribution',False),('firstExecutableLine',True),('methodCountersFromSame120Run',{})]:
 bad=copy.deepcopy(sample);bad[field]=value;assert json.dumps(bad,sort_keys=True)!=json.dumps(sample,sort_keys=True)
 try:row_contract(bad)
 except (AssertionError,KeyError):checks+=1
 else:raise AssertionError('false Layout reference accepted')
for k,v in [('sourceArtifacts',5),('codeClasses',5),('annotationOnly',0),('rawMethods',40),('officialMeasuredMethods',14),('standardGeneratedFilters',26),('existingActualCaseKeys',7)]:assert type(m[k]) is int and m[k]==v
assert all(m[k]==0 for k in ['productTestsExecuted','newProductTests','newJavaCompilerExecutions','sourceRegistryAcceptedDelta','newAcceptance']) and m['formalUpdated'] is False and m['effortRate'] is None
# BUG2555: original producer JSON is unchanged; preserve and identify its exact original tool.
import ast
beforeTool=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG24810-header-codec-console-before-v1/809_header_codec_method_trace.py';correctedTool=R/'evidence/01_PT/018_NK-OPS-001/input/809_header_codec_method_trace.py';assert sha(beforeTool)==m['toolSha256'];beforeAst=ast.parse(beforeTool.read_text());afterAst=ast.parse(correctedTool.read_text());assert len(beforeAst.body)==len(afterAst.body) and all(ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False) for a,b in zip(beforeAst.body[:-1],afterAst.body[:-1]))
counts=next(n for n in ast.walk(afterAst.body[-1]) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='dict');kw={k.arg:ast.unparse(k.value) for k in counts.keywords};assert kw['methods']=='len(rows)' and kw['filters']=='len(filtered)' and kw['caseRefs']=='len(cases)'
assert len(rows)==m['officialMeasuredMethods']==14 and len(filtered)==m['standardGeneratedFilters']==26 and len(cases)==7
assert sum('BRANCH' not in c['counters'] for c in classes)==2
O.mkdir(); out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],testSource=cfg['testSource'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),sourceArtifacts=5,physicalClasses=5,codeClasses=5,annotationOnly=0,rawMethods=40,officialMeasuredMethods=14,standardGeneratedFilters=26,existingActualCaseKeys=7,coverageReferences=total,metadataNegativeChecks=checks,exclusiveRdOwnershipUnchanged=True,naturalZeroBranchSources=2,originalProducerJsonUnchanged=True,originalProducerTool=dict(path=str(beforeTool.relative_to(R)),sha256=sha(beforeTool)),correctedConsoleTool=dict(path=str(correctedTool.relative_to(R)),sha256=sha(correctedTool)),consoleCountCorrectedByComputedLengths=True,perCaseProbeAttribution=None,methodRelationsBoundOnly=True,allBranchOraclesIndividuallyVerified=False,productTestsExecuted=0,newProductTests=0,newJavaCompilerExecutions=0,sourceRegistryAcceptedDelta=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,methods=14,filters=26,cases=7,metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
