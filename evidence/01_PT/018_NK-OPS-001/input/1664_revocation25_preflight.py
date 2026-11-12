from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';W=R.parent/'pgpt-runs/PG379/pg27498-revocation25-normal-v1';O=B/'evidence/PG27506-revocation25-preflight-v1';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();pp=B/'evidence/PG27498-revocation25-normal-v1/manifest.json';m=ld(pp);assert m['actualExit']==0 and m['expectedTests']==25 and len(m['selectedClasses'])==4 and m['MainSourceSubsetCount']==9
for p,h in m['inputHashes'].items():assert sha(R/p)==h
for p,h in m['dependencies'].items():assert sha(Path(p))==h
for folder,key in [('component','physicalClassHashes'),('target/classes','mainClassHashes'),('test-classes','testClassHashes')]:assert m[key]=={str(p.relative_to(W/folder)):sha(p) for p in (W/folder).rglob('*.class')}
assert len(m['physicalClassHashes'])==9 and m['mainClassHashes']==m['physicalClassHashes'];assert len(m['dependencies'])==2 and all('jspecify/' in p or p.endswith('junit-platform-console-standalone-1.13.4.jar') for p in m['dependencies'])
ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;original=next(p for p in ET.parse(R/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');copied=ET.parse(W/'pom.xml').getroot().find('.//'+tag('plugin'));assert ET.tostring(original)==ET.tostring(copied) and sha(W/'pom.xml')==m['subsetPomSha256'];assert '-Xep:NullAway:ERROR' in ET.tostring(copied).decode() and '-Werror' in ET.tostring(copied).decode()
sp=B/'evidence/PG27500-revocation25-static-v1/manifest.json';st=ld(sp);assert st['actualExit']==0 and st['inputHashes']==m['inputHashes'] and not st['processingErrors'] and st['checkstyleFindings']==0 and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors']);expected={*[('PendingRevocationFatalPortTest.java','UseProperClassLoader',x) for x in ['114','129','150']],('PendingRevocationPortTest.java','CloseResource','495'),('PendingRevocationPortTest.java','DoNotThrowExceptionInFinally','525'),*[('PendingRevocationPortTest.java','DoNotUseThreads',x) for x in ['495','498','507','526','527']],*[('PendingRevocationPortTest.java','UseConcurrentHashMap',x) for x in ['594','596']],('PendingRevocationPortTest.java','UseProperClassLoader','686')};assert len(expected)==13 and {(Path(x['path']).name,x['rule'],x['line']) for x in st['rawFindings']}==expected
classified=[]
for x in st['rawFindings']:
 if x['rule']=='UseProperClassLoader':reason='StandaloneJUnit explicitJDK JDBCinterface Proxy loader; noJ2EE/container/contextloader accessors.'
 elif x['rule']=='UseConcurrentHashMap':reason='PrivateFixture maps confined tosingleworker; parallelbranches eachcreateownFixture, repository itselfstateless andJUnitparallel disabled.'
 elif x['rule']=='CloseResource':reason='OwnedJUnitexecutorfinallyshutdownNow/await10 bounded; TWRwouldrestoreunboundedclose.'
 elif x['rule']=='DoNotThrowExceptionInFinally':reason='Unconfirmedownedworker mustfailJUnit notcountasPASS/resourcesreleased.'
 else:reason='StandaloneJUnit own2workers/Future5/finallyawait10; no server/container/businessDB threads.'
 classified.append(dict(**x,disposition='NOT_APPLICABLE_EXPLICIT_ORDINARY_TEST_CONTEXT_NO_SUPPRESSION',reason=reason))
fxPath=B/'evidence/PG27494-revocation-port-finite-source-v1/manifest.json';fx=ld(fxPath);assert fx['actualExit']==0 and fx['originalAllAssertionsInverseExact'] and sha(R/fx['path'])==fx['newSha256'];inverse=(R/fx['path']).read_text()
for change in reversed(fx['changes']):assert inverse.count(change['after'])==1;inverse=inverse.replace(change['after'],change['before'])
assert hashlib.sha256(inverse.encode()).hexdigest()==fx['oldSha256']
for manifest,stages in [(pp,m['stages']),(sp,st['stages'])]:
 for label,v in stages.items():
  assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(manifest.parent/(label+'.'+stream))==v[stream+'Sha256']
assert set(m['mainClassHashes'])=={n.replace('.','/')+'.class' for n in st['spotbugs']['classStats']}
style=B/'evidence/PG22122-current7aed-lineage-style-v1/manifest.json';ms=ld(style);assert ms['actualExit']==ms['applicableViolations']==ms['unclassified']==ms['checkstyle']==0;arts=style.parent/'artifacts.json';assert sha(arts)==ms['files']['artifacts.json'];rows={x['path']:x for x in ld(arts)}
for p in m['apiMainSources']:
 if Path(p).name!='PendingRevocationRepository.java':assert rows[p]['sha256']==m['inputHashes'][p]
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(n.endswith('/'+h+'.class') for n in m['physicalClassHashes'] for h in held);assert not any(any(x in (R/p).read_text() for x in held+['@BeforeAll','@TempDir','DriverManager','DataSource','java.nio.file','ProcessBuilder']) for p in m['apiTestSources']);normal=ld(B/'evidence/PG22106-api-stop-static-independent-input-v1/normal.json')
for p in m['apiTestSources']:
 if Path(p).name not in ['PendingRevocationFatalPortTest.java','PendingRevocationPortTest.java']:assert m['inputHashes'][p]==hashlib.sha256(__import__('subprocess').check_output(['git','show','922df4cdb2e9954627e879d6f864e13d67cadceb:'+p])).hexdigest()
O.mkdir();v=dict(actualExit=0,inputHashes=m['inputHashes'],prepare=ref(pp),testAndChangedMainStatic=ref(sp),unchangedMainStyle=ref(style),finiteOriginalAssertions=ref(fxPath),classified=classified,expectedTests=25,fullPhysicalClasses=9,newDefinitions=5,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,pmdRawFindings=13,manualSuppressionAdded=False,actualBackendOrHeldClassActions=0,heldFixturesExtractedOrRewritten=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,fullReportExpectedPartial=True,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,manifest=ref(O/'manifest.json'))))
