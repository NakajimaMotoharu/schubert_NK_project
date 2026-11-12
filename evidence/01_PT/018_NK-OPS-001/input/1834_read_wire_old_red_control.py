"""Independent old-source oracle control: only three new public callback tests, no held entries."""
from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as ET,zipfile
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';W=R.parent/'pgpt-runs/PG379/pg27824-read-wire-normal40-v1';O=B/'evidence/PG27832-read-wire-old-source-red-control-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists()
m=ld(B/'evidence/PG27824-read-wire-normal40-v1/manifest.json');np=B/'evidence/PG22106-api-stop-static-independent-input-v1/normal.json';assert sha(np)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';normal=ld(np);baseline='7aed8eace7c844c2f79f2e39db766faf914890d5';assert normal['source']==baseline
for p in m['apiMainSources']:
 assert hashlib.sha256(subprocess.check_output(['git','show',baseline+':'+p])).hexdigest()==normal['begin']['inputHashes'][p]
assert not any(n.endswith('/'+h+'.class') for n in m['mainClassHashes'] for h in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
O.mkdir();oldjar=W/'read-wire-old-only18.jar';oldclasses={}
with zipfile.ZipFile(normal['jars']['web']['path']) as src,zipfile.ZipFile(oldjar,'w',compression=zipfile.ZIP_STORED) as dst:
 for n in m['mainClassHashes']:
  data=src.read(n);h=hashlib.sha256(data).hexdigest();assert h==normal['normalPhysicalClassHashes']['web:'+n];dst.writestr(n,data);oldclasses[n]=h
# No whole Web jar digest/scan, and no other entries are read or materialized.
methods=[x['name'][:-2] for x in m['expectedCases'] if x['classname'].endswith('.ProtectedReadFatalContractTest') and x['name'].startswith(('fatal001','fatal002','fatal003'))];assert len(methods)==3
klass='dev.codex.schubert.nk.web.messaging.ProtectedReadFatalContractTest';deps=m['dependencies'];jdk=TC/'jdk-25.0.4/bin';console=TC/'junit-platform-console-standalone-1.13.4.jar';c.SLOT=O
cmd=[str(jdk/'java'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Xlog:class+init=info:file='+str(O/'class-init.stdout'),'-jar',str(console),'execute','--disable-banner','--class-path',':'.join([str(oldjar),str(W/'test-classes'),*deps]),*[a for name in methods for a in ['--select-method',klass+'#'+name]],'--reports-dir',str(O/'xml'),'--fail-if-no-tests','--details','summary'];stage=c.step('red-control',cmd,W,timeout=60)
cases=[]
for p in (O/'xml').glob('TEST-*.xml'):
 for x in ET.parse(p).findall('testcase'):
  f=x.find('failure');cases.append(dict(classname=x.get('classname'),name=x.get('name'),failure=f is not None,error=x.find('error') is not None,skipped=x.find('skipped') is not None,message=f.get('message') if f is not None else None))
assert stage['actualExit']==1 and not stage['timedOut'] and len(cases)==3 and all(x['failure'] and not x['error'] and not x['skipped'] for x in cases)
assert all('ProtectedReadWireException' in x['message'] and 'AssertionError' in x['message'] for x in cases)
v=dict(actualExit=0,oracleControlStage=stage,oldSource=baseline,oldMetadata=ref(np),oldWhitelistedClassHashes=oldclasses,oldJarSha256=sha(oldjar),newTestInputHashes={p:m['inputHashes'][p] for p in m['apiTestSources'] if p.endswith('/ProtectedReadFatalContractTest.java')},expectedFailures=3,actualCases=cases,productPtPassAdded=0,coverageAdded=0,normalRunExecuted=False,actualHeldBinaryAccess=False,actualBackendActions=0,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,expectedRedFailures=3,passAdded=0,manifest=ref(O/'manifest.json'))))
