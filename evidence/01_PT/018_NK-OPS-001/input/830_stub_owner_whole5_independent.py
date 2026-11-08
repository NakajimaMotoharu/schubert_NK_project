"""Independent original Stub5 source/oracle/terminal/CRC/output and resource-owner retest post."""
from pathlib import Path
import copy,datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'pgpt-runs/PG379/pg24872-stub-owner-original-whole5-v1';RAW=B/'evidence/PG24872-stub-owner-original-whole5-v1';O=B/'evidence/PG24874-stub-owner-whole5-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=RAW/'manifest.json';assert sha(mp)=='70eccff09e6d3b349c935d4eda3e1b5eae8eb3df236e2119c40f51d74203f825' and sha(S/'manifest.json')==sha(mp);m=load(mp);assert m['actualExit']==0 and m['productTestsExecuted']==5 and m['source']=='9738ad03ae41b4c3a098ad77b7d2ed0b29f6b476' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
pfref=m['begin']['preflight'];assert sha(R/pfref['path'])==pfref['sha256'];pf=load(R/pfref['path']);assert pf['actualExit']==0 and m['begin']['dependencies']==pf['dependencies'] and m['begin']['inputHashes']==pf['inputHashes'] and m['begin']['targetClassHashes']==pf['targetClassHashes']
for path,digest in m['begin']['inputHashes'].items():assert sha(R/path)==digest==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+path])).hexdigest()
for path,digest in m['begin']['dependencies'].items():assert sha(Path(path))==digest
for name,stage in m['stages'].items():assert stage['actualExit']==0 and stage['timedOut'] is False and load(S/(name+'-exit.safe.json'))==stage
for n in ['compile','unit','coverage','execinfo','classinfo']:assert n in m['stages']
caseNames={'emptyAnswerAndClock','nullContracts','clockFailures','resultValueAndRedaction','concurrentCallsAndEvidence'};fqn='dev.codex.schubert.nk.api.application.question.StubAnswerProviderTest';actual=[];envs=[];safe=E.Element('testsuite',name=fqn,tests='5',failures='0',errors='0',skipped='0')
for filename,h in m['xmlHashes'].items():
 path=S/'xml'/filename;assert sha(path)==h;root=E.parse(path).getroot();properties={v.get('name'):v.get('value') for v in root.findall('./properties/property')}
 for t in root.findall('testcase'):
  assert t.get('classname')==fqn and not any(t.findall(n) for n in ['failure','error','skipped']);name=t.get('name').removesuffix('()');assert name in caseNames;actual.append(name);envs.append(properties);E.SubElement(safe,'testcase',classname=fqn,name=name+'()')
assert len(actual)==len(set(actual))==5 and set(actual)==caseNames and m['cases']==[dict(className=fqn,name=n+'()',nonPass=[]) for n in actual]
for v in envs:assert v['java.runtime.version'].startswith('25.0.4') and v['user.language']=='ja' and v['user.country']=='JP' and v['user.timezone']=='Asia/Tokyo'
reported={k:envs[0][k] for k in ['java.runtime.version','java.vendor','os.name','os.arch','os.version','user.language','user.country','user.timezone']};assert all(all(v[k]==reported[k] for k in reported) for v in envs)
expected='provider=STUB\nanswerLength=0\nclockReadsPerCall=1\nconcurrentCalls=64\nuniqueClockValues=64\nexternalCalls=0\nrawBodySaved=false\n';output=S/'target/question-stub-traces/PT-ASY-STB005.txt';assert not output.is_symlink() and output.read_bytes()==expected.encode('ascii')
xml=E.parse(S/'coverage.xml').getroot();classes={c.get('name'):c for c in xml.findall('.//class')};targets={k.removesuffix('.class') for k in pf['targetClassHashes']};assert set(classes)==targets;perClass={}
for n,c in classes.items():
 ct={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in c.findall('counter')};assert ct['LINE']==dict(covered=5,missed=0) and ct['METHOD']==dict(covered=2,missed=0) and ct['CLASS']==dict(covered=1,missed=0) and 'BRANCH' not in ct and all(v['missed']==0 for v in ct.values());perClass[n]=ct
cfg=load(B/'input/814_payload_semantic_method_trace_scope.json');assert sha(R/cfg['physicalIndex']['path'])==cfg['physicalIndex']['sha256'];index=load(R/cfg['physicalIndex']['path']);assert sha(R/cfg['metadataInventory']['path'])==cfg['metadataInventory']['sha256'];meta=load(R/cfg['metadataInventory']['path']);normalNames={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta};held={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta if Path(r['sourcePath']).stem in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']};assert len(held)==4
for name,digest in pf['targetClassHashes'].items():assert index[name.removesuffix('.class')]['sha256']==digest==sha(S/'component'/Path(name).name)
info=(S/'execinfo.stdout').read_text();sessions=re.findall(r'^Session "([^"]+)":',info,re.M);assert sessions==['PG24872-STUB-ORIGINAL-WHOLE5'];positive={};crc={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4] in normalNames and int(hit[2])>0:assert hit[4] not in positive;positive[hit[4]]=int(hit[2]);crc[hit[4]]=hit[1];assert index[hit[4]]['crc64']==hit[1]
assert set(positive)==targets and not set(positive)&held
initializers=set(re.findall(r"Initializing '([^']+)'",(S/'class-init.log').read_text()));assert not initializers&held
pre=load(R/pf['priorFixturePreflight']['path']);assert sha(R/pf['priorFixturePreflight']['path'])==pf['priorFixturePreflight']['sha256'] and pre['originalFiveTestsAndAssertionsRetained'] is True and pre['onlyOwnerAndEquivalentOutputLiteralFormattingChanged'] is True
appref=pf['staticApplicability'];assert sha(R/appref['path'])==appref['sha256'];app=load(R/appref['path']);assert app['rawPmdFindings']==5 and app['applicableViolations']==0 and app['checkstyleFindings']==0 and app['suppressionAdded'] is False
# Test-owned executor finally is finite; no claim that every global2177 target is closed.
text=(R/pf['testPath']).read_text();assert 'executor.invokeAll(tasks, 5, TimeUnit.SECONDS)' in text and 'finally {\n      executor.shutdownNow();\n      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS)' in text
sample=dict(actualExit=0,tests=5,caseNames=sorted(actual),source=m['source'],crc=crc,branchCoveragePercent=None,sourceFour100=False,heldFourInitializations=0,outputSha256=hashlib.sha256(expected.encode()).hexdigest())
def validate(v):
 assert type(v['actualExit']) is int and v['actualExit']==0 and type(v['tests']) is int and v['tests']==5 and v['caseNames']==sorted(caseNames) and v['source']==m['source'] and v['crc']==crc and v['branchCoveragePercent'] is None and v['sourceFour100'] is False and type(v['heldFourInitializations']) is int and v['heldFourInitializations']==0 and v['outputSha256']==sha(output)
validate(sample);checks=0
for key,value in [('actualExit',143),('tests',True),('caseNames',sorted(caseNames)[:-1]),('source','0'*40),('crc',{}),('branchCoveragePercent',100),('sourceFour100',True),('heldFourInitializations',1),('outputSha256','0'*64)]:
 bad=copy.deepcopy(sample);bad[key]=value;assert json.dumps(bad,sort_keys=True)!=json.dumps(sample,sort_keys=True)
 try:validate(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('invalid result accepted')
O.mkdir();E.ElementTree(safe).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True);(O/'coverage.xml').write_bytes((S/'coverage.xml').read_bytes());(O/'PT-ASY-STB005.txt').write_bytes(output.read_bytes());(O/'execinfo.safe.txt').write_text('\n'.join(n+' '+crc[n]+' positiveProbes='+str(positive[n]) for n in sorted(positive))+'\n')
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),preflight=pfref,tests=5,wholeFixtures=1,failures=0,errors=0,skipped=0,aborted=0,newProductTests=0,existingTestsRequalified=5,productTestsExecuted=0,originalWholeTestExecutedByProducer=True,originalFiveTestsAndAssertionsRetained=True,perClassCounters=perClass,measuredLmc100=True,naturalZeroBranchSources=2,branchCoveragePercent=None,strictNonemptySourceFourCounterGateExit=1,allSourceFour100=False,singleSession=True,oldExecUnion=False,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=2,heldFourInitializations=0,heldFourPositiveMainProbes=0,pmdRawFindings=5,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,staticApplicability=appref,metadataNegativeChecks=checks,reportedEnvironment=reported,publicOutputLiteralMatches=True,finiteExecutorOwnerRetested=True,globalYkt2177Closed=False,productFileOperations=False,testOwnNewSlotPublicEvidenceWrites=True,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');write(O/'manifest.json',value);print(json.dumps(dict(actualExit=0,existingTestsRequalified=5,positiveMain=2,held4init=0,metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
