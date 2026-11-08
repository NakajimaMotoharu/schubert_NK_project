"""Independent changed-fixture whole21; own run, original terminal exception and clone oracles."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as E
import zipfile

R=Path.cwd();B=R/'evidence/01_PT/005_NK-MSG-001';RUNS=R.parent/'pgpt-runs/PG379'
C=B/'input/038_jms_memory_bounded_scope.json';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(C)
U=RUNS/cfg['unitSlot'];P=RUNS/cfg['compileSlot'];S=RUNS/cfg['staticSlot'];O=B/'evidence/PG24242-jms-memory-bounded-twentyone-independent-v1';assert not O.exists()
m=load(U/'manifest.json');begin=m['begin'];assert begin==load(U/'begin.json')
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,21,0,0,0)
assert begin['newMethods']==0 and begin['requalifiedExistingMethods']==21
assert begin['selected']==list(cfg['testClasses'].values())
assert begin['source']=='e8552cd21bd8aa6d129f61b2711c854744bd684c'
for name,pin in begin['inputHashes'].items():assert sha(R/name)==pin==hashlib.sha256(subprocess.check_output(['git','show',begin['source']+':'+name])).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',begin['normalSource'],begin['source'],'--',':(glob)src/**/src/main/java/**/*.java']).strip()
for name,pin in begin['dependencies'].items():assert sha(Path(name))==pin
for label,stage in m['stages'].items():
    assert stage['actualExit']==0 and not stage['timedOut'] and stage==load(U/(label+'-exit.safe.json'))
    for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
command=m['stages']['unit']['command'];assert command.count('--select-class')==4 and '--select-method' not in command and '--scan-classpath' not in command
assert not any('--enable-native-access' in word for word in command)
assert any('append=false' in word and 'sessionid='+cfg['session'] in word for word in command)
expected={(cls,method+'()') for path,cls in cfg['testClasses'].items() for method in re.findall(r'@Test\s+void\s+(\w+)\s*\(', (R/path).read_text())}
assert len(expected)==21
actual=[];timings=[];environment={};xmlpins={}
for p in sorted((U/'xml').glob('TEST-*.xml')):
    xmlpins[p.name]=sha(p);tree=E.parse(p).getroot();assert not any(tree.findall('.//'+tag) for tag in ['failure','error','skipped'])
    for case in tree.findall('testcase'):
        actual.append((case.get('classname'),case.get('name')));timings.append(dict(classname=case.get('classname'),name=case.get('name'),seconds=case.get('time')))
    environment.update({p.get('name'):p.get('value') for p in tree.findall('./properties/property') if p.get('name') in ['os.name','os.arch','java.version','java.vendor','file.encoding','user.timezone']})
assert len(actual)==len(set(actual))==21 and set(actual)==expected
for phrase in ['21 tests found','21 tests started','21 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert phrase in (U/'unit.stdout').read_text()
pfpath=R/cfg['preflightManifest'];pf=load(pfpath);assert pf['actualExit']==0 and pf['inputHashes']==begin['inputHashes']
assert pf['applicableStaticViolations']==0 and pf['pmdRawFindings']==14 and pf['checkstyleFindings']==pf['processingErrors']==0
assert pf['allOriginalTestOtherTokensAndOraclesPreserved'] and pf['noTimeoutPromiseMutation'] and pf['noNewFixtureOrMethodExtraction']
assert sha(P/'manifest.json')==begin['compileManifestSha256']==pf['compileManifestSha256']
assert sha(S/'manifest.json')==pf['staticManifestSha256']
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';nm=load(normal);assert sha(normal)==begin['normalManifestSha256']==pf['normalManifestSha256']
assert begin['normalSource']==nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
index=load(R/pf['normalPositiveMainIndex']['path']);assert sha(R/pf['normalPositiveMainIndex']['path'])==pf['normalPositiveMainIndex']['sha256']
physical={n:row['sha256'] for n,row in index.items() if row['path'] in cfg['mainPaths']};assert len(physical)==5 and physical==cfg['currentMainPhysical']==m['physical']
ids={n:index[n]['crc64'] for n in physical}
with zipfile.ZipFile(nm['jars']['web']['path']) as z:
    for n,h in physical.items():assert hashlib.sha256(z.read(n+'.class')).hexdigest()==sha(U/'component'/(n+'.class'))==h
info={name:identity for identity,name in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())};assert info==ids
ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "'+cfg['session']+'"' in ex
probes={n:[identity,int(hits),int(total)] for identity,hits,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
test_prefixes=[v.replace('.','/') for v in cfg['testClasses'].values()]
positive={n for n,v in probes.items() if v[1]>0 and n.startswith('dev/codex/schubert/nk/') and not any(n==p or n.startswith(p+'$') for p in test_prefixes)}
assert len(positive)==6 and set(physical)<=positive and all(n in index and probes[n][0]==index[n]['crc64'] for n in positive)
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']
assert not any(n.split('/')[-1].split('$')[0] in held for n in positive)
initialized=re.findall(r"Initializing '([^']+)'",(U/'class-init.log').read_text())
assert not any(name in n for name in held for n in initialized)
coverage_tree=E.parse(U/'coverage.xml').getroot();classes={x.get('name'):x for x in coverage_tree.findall('.//class')};assert set(classes)==set(physical)
coverage={}
for name in ['LINE','METHOD','CLASS','BRANCH']:
    rows=[x for x in coverage_tree.findall('counter') if x.get('type')==name];assert len(rows)==1
    c=rows[0];value=dict(covered=int(c.get('covered')),missed=int(c.get('missed')));assert value==dict(covered=cfg['expectedCoverage'][name],missed=0);coverage[name]=value
for cls in classes.values():
    assert all(int(c.get('missed'))==0 for c in cls.findall('counter'))
    for method in cls.findall('method'):assert all(int(c.get('missed'))==0 for c in method.findall('counter'))
# Separate forward recipe from preserved old Tests, independent of preflight's inverse.
def token_text(value):
    assert '"""' not in value
    return ''.join(re.findall(r'"(?:\\.|[^"\\])*"|\S',value))


def one(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


def forward(filename,old):
    text=token_text(old)
    if filename=='JmsRequestReplyClientTest.java':return one(text,'latch.await();','assertTrue(latch.await(5,TimeUnit.SECONDS));')
    if filename=='ReplyCorrelationRegistryTest.java':
        for name,expression,statement in [('firstCompletion','pending.completion().toCompletableFuture()','byte[]received={}.join();'),('secondCompletion','pending.completion().toCompletableFuture()','assertArrayEquals(newbyte[]{{1,2,3}},{}.join());'),('completion','pending.completion().toCompletableFuture()','assertEquals(1,{}.join().length);')]:
            before=statement.format(expression);after='var'+name+'='+expression+';assertTrue('+name+'.isDone());'+statement.format(name);text=one(text,before,after)
        marker='privatestaticvoidassertExceptional(PendingReplypending,Class<?extendsThrowable>cause){'
        text=one(text,marker,marker+'varcompletion=pending.completion().toCompletableFuture();assertTrue(completion.isDone());')
        return one(text,'assertThrows(RuntimeException.class,()->pending.completion().toCompletableFuture().join())','assertThrows(RuntimeException.class,completion::join)')
    marker='@TestvoidconcurrentRegistrationsRespectCapacityAndReuseAllSlots()'
    assert text.count(marker)==1;part,tail=text.split(marker,1)
    part=one(part,'if(completed){','varcompletion=pending.completion().toCompletableFuture();assertTrue(completion.isDone());if(completed){')
    part=one(part,'()->pending.completion().toCompletableFuture().join()','completion::join')
    part=one(part,'pending.completion().toCompletableFuture().join()','completion.join()');text=part+marker+tail
    for name,statement in [('firstCompletion','byte[]received={}.join();'),('secondCompletion','assertArrayEquals(newbyte[]{{7,8,9}},{}.join());')]:
        expression='timely.completion().toCompletableFuture()'
        text=one(text,statement.format(expression),'var'+name+'='+expression+';assertTrue('+name+'.isDone());'+statement.format(name))
    text=one(text,'CompletionExceptionfailure=assertThrows(CompletionException.class,()->late.completion().toCompletableFuture().join());','varlateCompletion=late.completion().toCompletableFuture();assertTrue(lateCompletion.isDone());CompletionExceptionfailure=assertThrows(CompletionException.class,lateCompletion::join);')
    s='assertArrayEquals(newbyte[]{7,8,9},independent.join());';text=one(text,s,'assertTrue(independent.isDone());'+s)
    return one(text,'assertArrayEquals(newbyte[]{7,8,9},pending.completion().toCompletableFuture().join());','varfinalCompletion=pending.completion().toCompletableFuture();assertTrue(finalCompletion.isDone());assertArrayEquals(newbyte[]{7,8,9},finalCompletion.join());')


for filename in cfg['changedTestSources']:
    old=(R/cfg['beforeDirectory']/filename).read_text();path=next(Path(p) for p in cfg['testClasses'] if Path(p).name==filename)
    assert forward(filename,old)==token_text((R/path).read_text())
assert pf['terminalJoinSites']==11 and pf['exactViewCompletionGuards']==10 and pf['noTimeoutPromiseMutation'] is True
constant_path=B/'evidence/PG24237-jms-constant-reference-javap-v1/manifest.json';constant=load(constant_path)
assert constant['actualExit']==0 and constant['normalWebJarSha256']==nm['jars']['web']['sha256']
assert constant['constantOwnerInstructionsAbsent'] is True and 'LayoutDefinition' not in (constant_path.parent/'metadata.stdout').read_text()
assert not any('protocol/layout/LayoutDefinition' in n for n in initialized)

O.mkdir();safe=E.Element('testsuite',name='PG24240_JMS_BOUNDED',tests='21',failures='0',errors='0',skipped='0')
for row in timings:E.SubElement(safe,'testcase',**{k:row[k] for k in ['classname','name']},time=row['seconds'])
E.ElementTree(safe).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True)
for src,name in [(U/'manifest.json','original-manifest.json'),(P/'manifest.json','compile-manifest.json'),(S/'manifest.json','static-manifest.json'),(pfpath,'preflight-manifest.json'),(U/'begin.json','begin.safe.json')]:shutil.copyfile(src,O/name)
for name in ['coverage.xml','classinfo.stdout','execinfo.stdout','jacoco.exec','unit.stdout','unit.stderr']:shutil.copyfile(U/name,O/name)
result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),branch='dev-foundation',source=begin['source'],productionCoreMain=nm['source'],sourceMainUnchanged=True,expectedMethods=21,tests=21,testClasses=4,failures=0,errors=0,skipped=0,aborted=0,requalifiedExistingTests=21,newUniqueTests=0,sourcePrograms=4,physicalClasses=5,coverage=coverage,wholeTargetApplicableCoverage100=True,allOriginalMethodAndOracleBytesPreserved=True,sourceInverseVerified=True,rawTargetProbeHits={n:probes[n] for n in physical},rawProbeAll100Required=False,onlyOfficialCoverageEngineFilters=True,manualCounterExclusions=[],oldExecUnion=False,singleSession=cfg['session'],observedPositiveMainClasses=6,allObservedMainCrcMatchCurrentNormal=True,heldFourPositiveMainProbes=0,heldFourInitializations=0,pmdRawFindings=14,pmdApplicableViolations=0,checkstyleFindings=0,staticProcessingErrors=0,suppressionAdded=False,finiteLatchSeconds=5,terminalJoinSites=11,exactViewCompletionGuards=10,independentForwardSourceRecipeVerified=True,noTimeoutPromiseMutation=True,normalTerminationAsserted=True,actualExternalBackendOrRootOrVmOrNativeOperations=False,noNewFixtureOrMethodExtraction=True,originalXmlPins=xmlpins,caseTimings=timings,reportedEnvironment=environment,sourceInputHashes=begin['inputHashes'],newAcceptance=0,formalUpdated=False,effortRate=None,productTestsExecuted=21,globalYktWaitSafetyAccepted=False,bugs=['BUG-2522'],ykts=['YKT-2177'],global451Accepted=False,files={p.name:sha(p) for p in O.iterdir()},verifier={'path':str(Path(__file__)),'sha256':sha(Path(__file__))})
(O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,tests=21,coverage=coverage,observedMain=6,heldFourInitializations=0,manifestSha256=sha(O/'manifest.json'))))
