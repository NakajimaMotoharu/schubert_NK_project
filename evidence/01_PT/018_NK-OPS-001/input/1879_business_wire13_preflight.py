"""Independent six-source, exact cached17 and intact whole13 static/closure preflight."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET,zipfile
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';W=R.parent/'pgpt-runs/PG379/pg27896-business-wire13-normal-v1';O=B/'evidence/PG27900-business-wire13-preflight-v1';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();pp=B/'evidence/PG27896-business-wire13-normal-v1/manifest.json';m=ld(pp);assert m['actualExit']==0 and m['expectedTests']==13 and len(m['selectedClasses'])==1 and m['MainSourceSubsetCount']==6
for p,h in m['inputHashes'].items():assert sha(R/p)==h
for p,h in m['dependencies'].items():assert sha(Path(p))==h
for folder,key in [('component','physicalClassHashes'),('target/classes','mainClassHashes'),('test-classes','testClassHashes')]:assert m[key]=={str(p.relative_to(W/folder)):sha(p) for p in (W/folder).rglob('*.class')}
assert len(m['physicalClassHashes'])==199 and len(m['mainClassHashes'])==6
cp=R/m['reusedRootPrepare']['path'];cache=ld(cp);assert sha(cp)==m['reusedRootPrepare']['sha256'];cf=R/m['reusedRootPreflight']['path'];cachedStatic=ld(cf);assert sha(cf)==m['reusedRootPreflight']['sha256'] and cachedStatic['actualExit']==0 and all(cachedStatic[k]==0 for k in ['staticApplicable','unclassified','processingErrors','checkstyle','spotbugs'])
package='dev/codex/schubert/nk/web/messaging/package-info.class';cache17={n:h for n,h in cache['mainClassHashes'].items() if n!=package};assert len(cache17)==17 and m['mainClassHashes'][package]==cache['mainClassHashes'][package]
for p in cache['apiMainSources']:assert sha(R/p)==cache['inputHashes'][p]==m['inputHashes'][p]
with zipfile.ZipFile(W/'cached-read-root17.jar') as archive:
 assert set(archive.namelist())==set(cache17)
 for n,h in cache17.items():assert hashlib.sha256(archive.read(n)).hexdigest()==h==m['physicalClassHashes'][n]
ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;compiler=next(p for p in ET.parse(R/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');copied=ET.parse(W/'pom.xml').getroot().find('.//'+tag('plugin'));assert ET.tostring(compiler)==ET.tostring(copied) and sha(W/'pom.xml')==m['subsetPomSha256'];assert hashlib.sha256(ET.tostring(copied)).hexdigest()==cache['rootCompilerSha256'] and '-Xep:NullAway:ERROR' in ET.tostring(copied).decode() and '-Werror' in ET.tostring(copied).decode()
sp=B/'evidence/PG27898-business-wire13-static-v1/manifest.json';st=ld(sp);assert st['actualExit']==0 and st['inputHashes']==m['inputHashes'] and not st['processingErrors'] and st['checkstyleFindings']==0 and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
test=R/m['apiTestSources'][0];lines=test.read_text().splitlines();anchors={'pool':'var pool = Executors.newFixedThreadPool(8);','submit':'.submit(','stop':'pool.shutdownNow();','join':'assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));'};positions={}
for k,t in anchors.items():
 found=[str(i+1) for i,line in enumerate(lines) if t in line];assert len(found)==1;positions[k]=found[0]
expected={('CloseResource',positions['pool']),*[('DoNotUseThreads',x) for x in positions.values()]};assert len(st['rawFindings'])==5 and {(x['rule'],x['line']) for x in st['rawFindings']}==expected and all(Path(x['path']).name=='WebBusinessWireClientsTest.java' for x in st['rawFindings']);classified=[dict(**x,disposition='NOT_APPLICABLE_OWNED_STANDALONE_JUNIT_NO_SUPPRESSION',reason='One owned fixed8worker pool/180tasks, every Future.get10/finallyshutdownNow/assertawait10; no application or broker threads') for x in st['rawFindings']]
for manifest,stages in [(pp,m['stages']),(sp,st['stages'])]:
 for label,v in stages.items():
  assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(manifest.parent/(label+'.'+stream))==v[stream+'Sha256']
assert set(m['mainClassHashes'])=={n.replace('.','/')+'.class' for n in st['spotbugs']['classStats']}
assert not any(n.endswith('/'+h+'.class') for n in m['physicalClassHashes'] for h in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
O.mkdir();v=dict(actualExit=0,inputHashes=m['inputHashes'],prepare=ref(pp),static=ref(sp),reusedRootPrepare=ref(cp),reusedRootPreflight=ref(cf),reusedPhysicalClasses=17,freshMain6IncludesSamePackageInfo=True,expectedTests=13,newDefinitions=0,fullPhysicalClasses=199,rootCompilerUnchanged=True,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,pmdRawFindings=5,classified=classified,independentSourceAnchors=positions,manualSuppressionAdded=False,actualBackendOrHeldClassActions=0,heldFixturesExtractedOrRewritten=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,fullReportExpectedPartial=True,naturalBranchZeroNotStrictFour100=True,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,manifest=ref(O/'manifest.json'))))
