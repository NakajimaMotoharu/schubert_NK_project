"""Independent changed-fixture whole15 qualification; only own new run and fixed public metadata."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as E
import zipfile

R=Path.cwd();B=R/'evidence/01_PT/015_NK-WEB-001';RUNS=R.parent/'pgpt-runs/PG379'
C=B/'input/050_menu_audit_bounded_scope.json';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(C)
U=RUNS/cfg['unitSlot'];P=RUNS/cfg['compileSlot'];S=RUNS/cfg['staticSlot'];O=B/'evidence/PG24222-menu-audit-bounded-fifteen-independent-v1';assert not O.exists()
m=load(U/'manifest.json');begin=m['begin'];assert begin==load(U/'begin.json')
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,15,0,0,0)
assert begin['newMethods']==0 and begin['requalifiedExistingMethods']==15
assert begin['selected']==list(cfg['testClasses'].values())
assert begin['source']=='f72114ac1c9e95a5ecc4d7286def4a3b554fcdee'
for name,pin in begin['inputHashes'].items():assert sha(R/name)==pin==hashlib.sha256(subprocess.check_output(['git','show',begin['source']+':'+name])).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',begin['normalSource'],begin['source'],'--',':(glob)src/**/src/main/java/**/*.java']).strip()
for name,pin in begin['dependencies'].items():assert sha(Path(name))==pin
for label,stage in m['stages'].items():
    assert stage['actualExit']==0 and not stage['timedOut'] and stage==load(U/(label+'-exit.safe.json'))
    for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
command=m['stages']['unit']['command'];assert command.count('--select-class')==2 and '--select-method' not in command and '--scan-classpath' not in command
assert not any('--enable-native-access' in word for word in command)
assert any('append=false' in word and 'sessionid='+cfg['session'] in word for word in command)
expected={(cls,method+'()') for path,cls in cfg['testClasses'].items() for method in re.findall(r'@Test\s+void\s+(\w+)\s*\(', (R/path).read_text())}
assert len(expected)==15
actual=[];timings=[];environment={};xmlpins={}
for p in sorted((U/'xml').glob('TEST-*.xml')):
    xmlpins[p.name]=sha(p);tree=E.parse(p).getroot();assert not any(tree.findall('.//'+tag) for tag in ['failure','error','skipped'])
    for case in tree.findall('testcase'):
        actual.append((case.get('classname'),case.get('name')));timings.append(dict(classname=case.get('classname'),name=case.get('name'),seconds=case.get('time')))
    environment.update({p.get('name'):p.get('value') for p in tree.findall('./properties/property') if p.get('name') in ['os.name','os.arch','java.version','java.vendor','file.encoding','user.timezone']})
assert len(actual)==len(set(actual))==15 and set(actual)==expected
for phrase in ['15 tests found','15 tests started','15 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert phrase in (U/'unit.stdout').read_text()
pfpath=R/cfg['preflightManifest'];pf=load(pfpath);assert pf['actualExit']==0 and pf['inputHashes']==begin['inputHashes']
assert pf['applicableStaticViolations']==0 and pf['pmdRawFindings']==11 and pf['checkstyleFindings']==pf['processingErrors']==0
assert pf['allOriginalTestOtherBytesPreserved'] and pf['finiteOwnerShutdown'] and pf['noNewFixtureOrMethodExtraction']
assert sha(P/'manifest.json')==begin['compileManifestSha256']==pf['compileManifestSha256']
assert sha(S/'manifest.json')==pf['staticManifestSha256']
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';nm=load(normal);assert sha(normal)==begin['normalManifestSha256']==pf['normalManifestSha256']
assert begin['normalSource']==nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
index=load(R/pf['normalPositiveMainIndex']['path']);assert sha(R/pf['normalPositiveMainIndex']['path'])==pf['normalPositiveMainIndex']['sha256']
physical={n:row['sha256'] for n,row in index.items() if row['path'] in cfg['mainPaths']};assert len(physical)==4 and physical==cfg['currentMainPhysical']==m['physical']
ids={n:index[n]['crc64'] for n in physical}
with zipfile.ZipFile(nm['jars']['web']['path']) as z:
    for n,h in physical.items():assert hashlib.sha256(z.read(n+'.class')).hexdigest()==sha(U/'component'/(n+'.class'))==h
info={name:identity for identity,name in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())};assert info==ids
ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "'+cfg['session']+'"' in ex
probes={n:[identity,int(hits),int(total)] for identity,hits,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
test_prefixes=[v.replace('.','/') for v in cfg['testClasses'].values()]
positive={n for n,v in probes.items() if v[1]>0 and n.startswith('dev/codex/schubert/nk/') and not any(n==p or n.startswith(p+'$') for p in test_prefixes)}
assert len(positive)==20 and set(physical)<=positive and all(n in index and probes[n][0]==index[n]['crc64'] for n in positive)
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
# Independent inverse: no original matrix, principal or business expectation was edited.
menu=R/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/MenuAuditContractTest.java';source=menu.read_bytes();original=(R/cfg['before']).read_bytes()
changed=b'      var workers = Executors.newFixedThreadPool(1);\n      try {\n        workers.submit(WebRequestTrace::markMenuViewed).get(10, TimeUnit.SECONDS);\n      } finally {\n        workers.shutdownNow();\n        assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));\n      }'
old=b'      try (var workers = Executors.newFixedThreadPool(1)) {\n        workers.submit(WebRequestTrace::markMenuViewed).get();\n      }'
assert source.count(changed)==1 and source.replace(changed,old,1).replace(b'import java.util.concurrent.TimeUnit;\n',b'',1)==original
O.mkdir();safe=E.Element('testsuite',name='PG24220_MENU_BOUNDED',tests='15',failures='0',errors='0',skipped='0')
for row in timings:E.SubElement(safe,'testcase',**{k:row[k] for k in ['classname','name']},time=row['seconds'])
E.ElementTree(safe).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True)
for src,name in [(U/'manifest.json','original-manifest.json'),(P/'manifest.json','compile-manifest.json'),(S/'manifest.json','static-manifest.json'),(pfpath,'preflight-manifest.json'),(U/'begin.json','begin.safe.json')]:shutil.copyfile(src,O/name)
for name in ['coverage.xml','classinfo.stdout','execinfo.stdout','jacoco.exec','unit.stdout','unit.stderr']:shutil.copyfile(U/name,O/name)
result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),branch='dev-foundation',source=begin['source'],productionCoreMain=nm['source'],sourceMainUnchanged=True,expectedMethods=15,tests=15,testClasses=2,failures=0,errors=0,skipped=0,aborted=0,requalifiedExistingTests=15,newUniqueTests=0,sourcePrograms=3,physicalClasses=4,coverage=coverage,wholeTargetApplicableCoverage100=True,allOriginalMethodAndOracleBytesPreserved=True,sourceInverseVerified=True,rawTargetProbeHits={n:probes[n] for n in physical},rawProbeAll100Required=False,onlyOfficialCoverageEngineFilters=True,manualCounterExclusions=[],oldExecUnion=False,singleSession=cfg['session'],observedPositiveMainClasses=20,allObservedMainCrcMatchCurrentNormal=True,heldFourPositiveMainProbes=0,heldFourInitializations=0,pmdRawFindings=11,pmdApplicableViolations=0,checkstyleFindings=0,staticProcessingErrors=0,suppressionAdded=False,finiteFutureSeconds=10,finiteShutdownSeconds=10,normalTerminationAsserted=True,actualExternalBackendOrRootOrVmOrNativeOperations=False,noNewFixtureOrMethodExtraction=True,originalXmlPins=xmlpins,caseTimings=timings,reportedEnvironment=environment,sourceInputHashes=begin['inputHashes'],newAcceptance=0,formalUpdated=False,effortRate=None,productTestsExecuted=15,globalYktWaitSafetyAccepted=False,bugs=['BUG-2521'],ykts=['YKT-2177'],global451Accepted=False,files={p.name:sha(p) for p in O.iterdir()},verifier={'path':str(Path(__file__)),'sha256':sha(Path(__file__))})
(O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,tests=15,coverage=coverage,observedMain=20,heldFourInitializations=0,manifestSha256=sha(O/'manifest.json'))))
