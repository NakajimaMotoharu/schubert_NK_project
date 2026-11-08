"""Pin Immutable carrier static requirement/case references to existing normal run, never run Java."""
from pathlib import Path
import datetime, hashlib, json, re, subprocess, xml.etree.ElementTree as E

R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'
C=B/'input/776_carrier_method_trace_scope.json'; O=B/'evidence/PG24716-carrier-method14-trace-v1'
assert not O.exists()
load=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=load(C)
def pinned(ref):
 p=R/ref['path']; assert sha(p)==ref['sha256']; return load(p)
normal=pinned(cfg['normalProof']); inv=pinned(cfg['metadataInventory']); desc=pinned(cfg['descriptorInventory']); index=pinned(cfg['physicalIndex'])
assert normal['actualExit']==0 and normal['tests']==120 and normal['source']==cfg['testSource'] and normal['productionCoreMain']==cfg['source']
for ref in cfg['oracleDocuments']: assert sha(R/ref['path'])==ref['sha256']
parent=(R/cfg['normalProof']['path']).parent
for n in ['coverage.xml','testcases.safe.xml']: assert sha(parent/n)==normal['files'][n]
xml={r.get('name'):r for r in E.parse(parent/'coverage.xml').getroot().findall('.//class')}
actual={r.get('classname')+'#'+r.get('name') for r in E.parse(parent/'testcases.safe.xml').getroot().findall('testcase')}
assert len(actual)==120
cases={}
for label,c in cfg['cases'].items():
 assert c['caseKey'] in actual
 fqn,method=c['caseKey'].split('#'); method=method.removesuffix('()')
 p=R/'src/schubert-nk-protocol/src/test/java'/Path(fqn.replace('.','/')).with_suffix('.java')
 assert p.name in ['PayloadCodecTest.java','MessageCodecTest.java']
 assert hashlib.sha256(subprocess.check_output(['git','show',cfg['testSource']+':'+str(p.relative_to(R))])).hexdigest()==sha(p)
 lines=p.read_text().splitlines(keepends=True); starts=[i for i,l in enumerate(lines) if re.match(r'^  void '+re.escape(method)+r'\(',l)]; assert len(starts)==1
 start=starts[0]; end=next(i for i in range(start+1,len(lines)) if lines[i]=='  }\n'); body=''.join(lines[start:end+1]); assert 'assert' in body and '@Test' in ''.join(lines[max(0,start-2):start])
 cases[label]=dict(**c,path=str(p.relative_to(R)),sourceSha256=sha(p),declarationLine=start+1,bodyEndLine=end+1,assertionBodySha256=hashlib.sha256(body.encode()).hexdigest(),actual120PassCase=True,individualProbeAttribution=None)
owners={r['path']:r for r in desc}; selected=[r for r in inv if r['sourcePath'] in cfg['sourcePaths']]; assert len(selected)==11
task=next(r for r in load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks'] if r['id']==cfg['owner'])
assert set(cfg['sourcePaths'])<=set(task['ownedArtifacts']) and task['requirementIds']==[]
designs={}; approved=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip()
for p in [next((R/'documents/200_UI').rglob('232_*.md')),next((R/'documents/200_UI').rglob('233_*.md')),R/'documents/300_SS/320_メッセージング/322_固定長電文codec実装設計.md']:
 rel=str(p.relative_to(R)); assert hashlib.sha256(subprocess.check_output(['git','show',approved+':'+rel])).hexdigest()==sha(p); designs[rel]=dict(approvedMain=approved,sha256=sha(p))
rows=[]; classes=[]; filtered=[]; abstract=[]; raw_count=0; total={k:dict(covered=0,missed=0) for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}
for item in sorted(selected,key=lambda r:r['physicalKey']):
 path=item['sourcePath']; p=R/path; name=item['physicalKey'].split(':',1)[1].removesuffix('.class'); artifact=owners[path]
 assert artifact['owner']==artifact['costOwner']==item['owner']==cfg['owner'] and sha(p)==artifact['sha256']==item['sourceSha256']
 assert item['classSha256']==index[name]['sha256'] and item['metadataStatus']=='STATIC_METADATA_NOT_RUNTIME_OR_COVERAGE'
 assert hashlib.sha256(subprocess.check_output(['git','show',cfg['source']+':'+path])).hexdigest()==sha(p)
 methods=item['structure']['methods']; raw_count+=len(methods)
 if p.stem=='package-info':
  assert not methods and name not in xml and '@NullMarked' in p.read_text() and 'import org.jspecify.annotations.NullMarked;' in p.read_text()
  classes.append(dict(path=path,owner=cfg['owner'],costOwner=cfg['owner'],sourceSha256=sha(p),className=name,classSha256=item['classSha256'],crc64=index[name]['crc64'],status='ANNOTATION_ONLY_NO_METHOD_NO_CLASS_COVERAGE_CREDIT')); continue
 if not any(method['hasCode'] for method in methods):
  assert name.endswith(('/FieldValue','/LayoutPayload')) and all(method['hasCode'] is False for method in methods)
  for method in methods:abstract.append(dict(symbol=name+'#'+method['name']+method['descriptor'],rawMetadata=method,status='ABSTRACT_INTERFACE_CONTRACT_NO_EXECUTABLE_CODE',relatedCaseKeys=[cases['W1']['caseKey']],runtimeMethodCoverage=None))
  classes.append(dict(path=path,owner=cfg['owner'],costOwner=cfg['owner'],sourceSha256=sha(p),className=name,classSha256=item['classSha256'],crc64=index[name]['crc64'],status='DECLARATION_ONLY_NO_EXECUTABLE_METHOD_NO_COVERAGE_CREDIT')); continue
 xc=xml[name]; measured={(m.get('name'),m.get('desc')):m for m in xc.findall('method')}; counters={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xc.findall('counter')}
 assert all(v['missed']==0 for v in counters.values())
 for k in total:
  for t in ['covered','missed']: total[k][t]+=counters.get(k,{}).get(t,0)
 classes.append(dict(path=path,owner=cfg['owner'],costOwner=cfg['owner'],sourceSha256=sha(p),className=name,classSha256=item['classSha256'],crc64=index[name]['crc64'],counters=counters,branchStatus='MEASURED_NONEMPTY' if 'BRANCH' in counters else 'NATURAL_ZERO_NA_NOT_100'))
 for method in methods:
  key=(method['name'],method['descriptor']); symbol=name+'#'+''.join(key)
  if key not in measured:
   stem=name.split('/')[-1]
   if stem in cfg['standardEnumSymbols']:
    assert key[0] in ['values','valueOf','$values','<init>'] and 'enum Unset implements FieldValue' in p.read_text()
    reason='STANDARD_JACOCO_ENUM_GENERATED_METHOD_OR_EMPTY_CONSTRUCTOR_FILTER'
   else:
    assert key[0] in cfg['generatedMethods'][stem] and ('record '+stem.split('$')[-1]+'(') in p.read_text()
    reason='STANDARD_JACOCO_RECORD_GENERATED_METHOD_FILTER'
   filtered.append(dict(symbol=symbol,rawMetadata=method,status=reason,manualExclusion=False,artificialInvocation=False)); continue
  xm=measured[key]; rule=cfg['methodRules'][name.split('/')[-1]][key[0]]; casekeys=[cases[c]['caseKey'] for c in rule['cases']]
  assert casekeys and set(casekeys)<=actual and len(casekeys)<120
  ct={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xm.findall('counter')}; assert ct['METHOD']==dict(covered=1,missed=0) and all(v['missed']==0 for v in ct.values())
  rows.append(dict(symbol=symbol,className=name,method=key[0],descriptor=key[1],sourcePath=path,sourceSha256=sha(p),firstExecutableLine=int(xm.get('line')),owner=cfg['owner'],costOwner=cfg['owner'],relatedRd=rule['relatedRd'],ui=['232','233'],ss=['322'],ssSections=rule['ssSections'],contract=rule['contract'],staticPath=rule['staticPath'],caseLabels=rule['cases'],actualCaseKeys=casekeys,testIdAliases=sorted({i for c in rule['cases'] for i in cases[c]['testIds']}),methodCountersFromSame120Run=ct,perCaseProbeAttribution=None,allBranchOraclesIndividuallyVerified=False))
assert raw_count==39 and len(rows)==14 and len(filtered)==20 and len(abstract)==5 and len(classes)==11 and len(cases)==2
assert {k:total[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=36,METHOD=14,CLASS=6,BRANCH=16)
O.mkdir(); write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
for name,value in [('method-trace.json',rows),('case-oracles.json',cases),('class-trace.json',classes),('standard-filter.json',filtered),('abstract-contracts.json',abstract)]:write(O/name,value)
manifest=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source=cfg['source'],testSource=cfg['testSource'],config=dict(path=str(C.relative_to(R)),sha256=sha(C)),normalProof=cfg['normalProof'],sourceArtifacts=7,physicalClasses=11,codeClasses=6,annotationOnly=3,declarationOnlyInterfaces=2,abstractMethods=5,rawMethods=39,officialMeasuredMethods=14,standardGeneratedFilters=20,existingActualCaseKeys=2,coverageReferences=total,perCaseProbeAttribution=None,methodRelationsBoundOnly=True,allBranchOraclesIndividuallyVerified=False,newProductTests=0,productTestsExecuted=0,newJavaCompilerExecutions=0,productClassesInitialized=0,sourceRegistryAcceptedDelta=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,approvedDesigns=designs,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
write(O/'manifest.json',manifest);print(json.dumps(dict(actualExit=0,methods=14,filters=20,caseRefs=2,counters=total,manifestSha256=sha(O/'manifest.json'))))
