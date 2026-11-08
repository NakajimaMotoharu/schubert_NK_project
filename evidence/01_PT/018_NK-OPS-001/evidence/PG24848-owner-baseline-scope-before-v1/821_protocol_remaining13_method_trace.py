"""Pin remaining protocol static requirement/case references to existing normal run, never run Java."""
from pathlib import Path
import datetime, hashlib, json, re, subprocess, xml.etree.ElementTree as E

R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'
C=B/'input/820_protocol_remaining13_method_trace_scope.json'; O=B/'evidence/PG24838-protocol-remain13-method56-trace-v1'
assert not O.exists()
load=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=load(C)
def pinned(ref):
 p=R/ref['path']; assert sha(p)==ref['sha256']; return load(p)
normal=pinned(cfg['normalProof']); inv=pinned(cfg['metadataInventory']); desc=pinned(cfg['descriptorInventory']); index=pinned(cfg['physicalIndex'])
assert normal['actualExit']==0 and normal['tests']==120 and normal['source']==cfg['testSource'] and normal['productionCoreMain']==cfg['source']
for ref in cfg['oracleDocuments']: assert sha(R/ref['path'])==ref['sha256']
filterProof=pinned(cfg['standardFilterProof']); assert filterProof['actualExit']==0 and filterProof['officialFilterApplied'] is True
compilerProof={r['name']:r for r in filterProof['compilerRows']}
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
 assert p.name in ['LargeResultRecordCodecTest.java','MediaDescriptorValidatorTest.java','JstWireTimestampTest.java','BrokerTopologyTest.java','FailedJmsIsolationExceptionTest.java','UnconfirmedJmsRollbackExceptionTest.java']
 assert hashlib.sha256(subprocess.check_output(['git','show',cfg['testSource']+':'+str(p.relative_to(R))])).hexdigest()==sha(p)
 lines=p.read_text().splitlines(keepends=True); starts=[i for i,l in enumerate(lines) if re.match(r'^  void '+re.escape(method)+r'\(',l)]; assert len(starts)==1
 start=starts[0]; end=next(i for i in range(start+1,len(lines)) if lines[i]=='  }\n'); body=''.join(lines[start:end+1]); assert 'assert' in body and '@Test' in ''.join(lines[max(0,start-2):start])
 cases[label]=dict(**c,path=str(p.relative_to(R)),sourceSha256=sha(p),declarationLine=start+1,bodyEndLine=end+1,assertionBodySha256=hashlib.sha256(body.encode()).hexdigest(),actual120PassCase=True,individualProbeAttribution=None)
owners={r['path']:r for r in desc}; selected=[r for r in inv if r['sourcePath'] in cfg['sourcePaths']]; assert len(selected)==14
tasks={r['id']:r for r in load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks']}
assert set(cfg['sourcePaths'])==set(cfg['ownersBySource'])
for path,owner in cfg['ownersBySource'].items():assert path in tasks[owner]['ownedArtifacts']
designs={}; approved=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip()
for p in [*[next((R/'documents/200_UI').rglob(str(n)+'_*.md')) for n in [231,232,235,237]],*[next((R/'documents/300_SS').rglob(str(n)+'_*.md')) for n in [321,322,323,333,352]]]:
 rel=str(p.relative_to(R)); assert hashlib.sha256(subprocess.check_output(['git','show',approved+':'+rel])).hexdigest()==sha(p); designs[rel]=dict(approvedMain=approved,sha256=sha(p))
rows=[]; classes=[]; filtered=[]; abstract=[]; raw_count=0; total={k:dict(covered=0,missed=0) for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}
for item in sorted(selected,key=lambda r:r['physicalKey']):
 path=item['sourcePath']; owner=cfg['ownersBySource'][path]; p=R/path; name=item['physicalKey'].split(':',1)[1].removesuffix('.class'); artifact=owners[path]
 assert artifact['owner']==artifact['costOwner']==item['owner']==owner and sha(p)==artifact['sha256']==item['sourceSha256']
 assert item['classSha256']==index[name]['sha256'] and item['metadataStatus']=='STATIC_METADATA_NOT_RUNTIME_OR_COVERAGE'
 assert hashlib.sha256(subprocess.check_output(['git','show',cfg['source']+':'+path])).hexdigest()==sha(p)
 methods=item['structure']['methods']; raw_count+=len(methods)
 if p.stem=='package-info':
  assert not methods and name not in xml and '@NullMarked' in p.read_text() and 'import org.jspecify.annotations.NullMarked;' in p.read_text()
  classes.append(dict(path=path,owner=owner,costOwner=owner,sourceSha256=sha(p),className=name,classSha256=item['classSha256'],crc64=index[name]['crc64'],status='ANNOTATION_ONLY_NO_METHOD_NO_CLASS_COVERAGE_CREDIT')); continue
 if not any(method['hasCode'] for method in methods):
  assert name.endswith(('/ProtocolId','/WireEnum')) and all(method['hasCode'] is False for method in methods)
  for method in methods:abstract.append(dict(symbol=name+'#'+method['name']+method['descriptor'],rawMetadata=method,status='ABSTRACT_INTERFACE_CONTRACT_NO_EXECUTABLE_CODE',relatedCaseKeys=[cases['ID' if name.endswith('/ProtocolId') else 'EG']['caseKey']],runtimeMethodCoverage=None))
  classes.append(dict(path=path,owner=owner,costOwner=owner,sourceSha256=sha(p),className=name,classSha256=item['classSha256'],crc64=index[name]['crc64'],status='DECLARATION_ONLY_NO_EXECUTABLE_METHOD_NO_COVERAGE_CREDIT')); continue
 xc=xml[name]; measured={(m.get('name'),m.get('desc')):m for m in xc.findall('method')}; counters={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xc.findall('counter')}
 assert all(v['missed']==0 for v in counters.values())
 for k in total:
  for t in ['covered','missed']: total[k][t]+=counters.get(k,{}).get(t,0)
 classes.append(dict(path=path,owner=owner,costOwner=owner,sourceSha256=sha(p),className=name,classSha256=item['classSha256'],crc64=index[name]['crc64'],counters=counters,branchStatus='STANDARD_COMPILER_FILTERED_NOT_NATURAL_SOURCE_ZERO' if name in cfg['standardSwitchClasses'] else ('MEASURED_NONEMPTY' if 'BRANCH' in counters else 'NATURAL_ZERO_NA_NOT_100')))
 for method in methods:
  key=(method['name'],method['descriptor']); symbol=name+'#'+''.join(key)
  if key not in measured:
   stem=name.split('/')[-1]
   if name in cfg['standardSwitchClasses']:
    proof=compilerProof[name];assert proof['sha256']==item['classSha256'] and proof['crc64']==index[name]['crc64'] and key==('<clinit>','()V') and not measured and proof['syntheticSwitchMap'] is True and type(proof['officialMeasuredMethods']) is int and proof['officialMeasuredMethods']==0 and proof['manualExclusion'] is False
    reason='STANDARD_JACOCO_SYNTHETIC_SWITCHMAP_FILTER_PRIOR_SAME_BYTES'
   elif stem in cfg['privateUtilitySources']:
    assert key==('<init>','()V') and method['flags']==2 and method['codeLength']==5 and ('private '+stem+'() {}') in p.read_text()
    reason='STANDARD_JACOCO_PRIVATE_EMPTY_UTILITY_CONSTRUCTOR_FILTER'
   elif stem in cfg['standardEnumSources']:
    assert key[0] in ['values','valueOf','$values','<init>'] and ('public enum '+stem) in p.read_text()
    reason='STANDARD_JACOCO_ENUM_GENERATED_METHOD_OR_EMPTY_CONSTRUCTOR_FILTER'
   else:
    assert stem in cfg['generatedMethods'] and key[0] in cfg['generatedMethods'][stem] and ('public record '+stem+'(') in p.read_text()
    reason='STANDARD_JACOCO_RECORD_GENERATED_METHOD_FILTER'
   filtered.append(dict(symbol=symbol,rawMetadata=method,status=reason,manualExclusion=False,artificialInvocation=False)); continue
  xm=measured[key]; rules=cfg['methodRules'][name.split('/')[-1]];rule=rules.get(key[0]+'#'+key[1],rules[key[0]]); casekeys=[cases[c]['caseKey'] for c in rule['cases']]
  assert casekeys and set(casekeys)<=actual and len(casekeys)<120
  ct={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xm.findall('counter')}; assert ct['METHOD']==dict(covered=1,missed=0) and all(v['missed']==0 for v in ct.values())
  rows.append(dict(symbol=symbol,className=name,method=key[0],descriptor=key[1],sourcePath=path,sourceSha256=sha(p),firstExecutableLine=int(xm.get('line')),owner=owner,costOwner=owner,relatedRd=rule['relatedRd'],ui=cfg['referencesByOwner'][owner]['ui'],ss=cfg['referencesByOwner'][owner]['ss'],ssSections=rule['ssSections'],contract=rule['contract'],staticPath=rule['staticPath'],caseLabels=rule['cases'],actualCaseKeys=casekeys,testIdAliases=sorted({i for c in rule['cases'] for i in cases[c]['testIds']}),methodCountersFromSame120Run=ct,perCaseProbeAttribution=None,allBranchOraclesIndividuallyVerified=False))
assert raw_count==76 and len(rows)==56 and len(filtered)==20 and len(abstract)==0 and len(classes)==14 and len(cases)==28
assert {k:total[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=262,METHOD=56,CLASS=12,BRANCH=147)
O.mkdir(); write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
for name,value in [('method-trace.json',rows),('case-oracles.json',cases),('class-trace.json',classes),('standard-filter.json',filtered),('abstract-contracts.json',abstract)]:write(O/name,value)
manifest=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source=cfg['source'],testSource=cfg['testSource'],config=dict(path=str(C.relative_to(R)),sha256=sha(C)),normalProof=cfg['normalProof'],sourceArtifacts=13,physicalClasses=14,codeClasses=12,annotationOnly=1,declarationOnlyInterfaces=0,abstractMethods=0,rawMethods=76,officialMeasuredMethods=56,standardGeneratedFilters=20,existingActualCaseKeys=28,coverageReferences=total,perCaseProbeAttribution=None,methodRelationsBoundOnly=True,allBranchOraclesIndividuallyVerified=False,newProductTests=0,productTestsExecuted=0,newJavaCompilerExecutions=0,productClassesInitialized=0,sourceRegistryAcceptedDelta=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,approvedDesigns=designs,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
write(O/'manifest.json',manifest);print(json.dumps(dict(actualExit=0,methods=len(rows),filters=len(filtered),caseRefs=len(cases),counters=total,manifestSha256=sha(O/'manifest.json'))))
