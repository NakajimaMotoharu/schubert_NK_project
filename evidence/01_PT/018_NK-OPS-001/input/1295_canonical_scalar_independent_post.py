"""Original whole10 terminal, independent golden inputs and full5 physical/session/CRC/source proof."""
from pathlib import Path
import collections,datetime,hashlib,hmac,json,re,shutil,struct,subprocess,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';U=RUNS/'pg26646-canonical-whole10-v2';A=B/'evidence/PG26646-canonical-whole10-v2';W=RUNS/'pg26628-canonical-pure-main-v1';O=B/'evidence/PG26648-canonical-independent-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());assert not O.exists();m=load(A/'manifest.json');b=m['begin'];source='62960fc3b5d4a67cf7bd9df887b668169d10f87f';assert b['source']==b['productionCoreMain']==source;assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,10,0,0,0)
for p,h in b['inputHashes'].items():assert sha(R/p)==h==hashlib.sha256(subprocess.check_output(['git','show',source+':'+p])).hexdigest()
for p,h in b['dependencies'].items():assert sha(Path(p))==h
pf=B/'evidence/PG26644-canonical-pure-preflight-v2/manifest.json';f=load(pf);assert f['actualExit']==0 and f['inputHashes']==b['inputHashes'] and sha(pf)==b['preflightManifestSha256'];assert f['staticApplicable']==f['unclassified']==f['processingErrors']==f['checkstyle']==f['spotbugs']==0
for label,v in m['stages'].items():
 assert v['actualExit']==0 and not v['timedOut'] and v==load(A/(label+'-exit.safe.json'))
 for stream in ['stdout','stderr']:assert sha(A/(label+'.'+stream))==v[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==2 and '--select-method' not in cmd and '--scan-classpath' not in cmd;assert not any(x in str(cmd) for x in ['schubert-nk-api-0.1','schubert-nk-storage','schubert-nk-protocol-0.1','artemis','postgres','enable-native-access','excludes='])
expected={(x['classname'],x['name']) for x in b['expectedCases']};actual=[];environment={}
for p in (U/'xml').glob('TEST-*.xml'):
 rt=ET.parse(p).getroot();assert not any(rt.findall('.//'+k) for k in ['failure','error','skipped']);actual.extend((x.get('classname'),x.get('name')) for x in rt.findall('testcase'));environment.update({v.get('name'):v.get('value') for v in rt.findall('./properties/property') if v.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
assert len(actual)==10 and set(actual)==expected
out=(A/'unit.stdout').read_text()
for text in ['10 tests found','10 tests started','10 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert text in out
physical={str(p.relative_to(W/'target/classes')):sha(p) for p in (W/'target/classes').rglob('*.class')};assert physical==b['physicalClassHashes'] and len(physical)==5;assert not any(x in n for n in physical for x in ['FingerprintKeyRing','ResponseSnapshotCodec','TemporaryInfrastructureException','WebStartupException'])
def crc64(data):
 v=0
 for byte in data:
  v^=byte
  for _ in range(8):v=(v>>1)^0xd800000000000000 if v&1 else v>>1
 return f'{v:016x}'
ids={n.removesuffix('.class'):crc64((W/'target/classes'/n).read_bytes()) for n in physical}
ci={n:c for c,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(A/'classinfo.stdout').read_text())};noCode={n for n in ids if n.endswith('/package-info')};assert len(noCode)==1 and set(ci)==set(ids)-noCode and all(ids[n]==v for n,v in ci.items())
# Parse only own allowed package annotation class to prove actual JVM method_count0.
raw=(W/'target/classes'/(next(iter(noCode))+'.class')).read_bytes();assert raw[:4]==bytes.fromhex('cafebabe');count=struct.unpack_from('>H',raw,8)[0];offset=10;i=1
while i<count:
 tag=raw[offset];offset+=1
 if tag==1:length=struct.unpack_from('>H',raw,offset)[0];offset+=2+length
 elif tag in [3,4,9,10,11,12,17,18]:offset+=4
 elif tag in [5,6]:offset+=8;i+=1
 elif tag in [7,8,16,19,20]:offset+=2
 elif tag==15:offset+=3
 else:raise AssertionError(tag)
 i+=1
offset+=6;interfaces=struct.unpack_from('>H',raw,offset)[0];offset+=2+2*interfaces;fields=struct.unpack_from('>H',raw,offset)[0];assert fields==0;offset+=2;assert struct.unpack_from('>H',raw,offset)[0]==0
ex=(A/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG26646-CANONICAL-WHOLE10"' in ex;probes={n:(c,int(hit),int(total)) for c,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};testPrefixes=[x.replace('.','/') for x in b['selectedClasses']];product={n for n in probes if n.startswith('dev/codex/schubert/nk/') and not any(n.startswith(t) for t in testPrefixes)};assert product==set(ci)
assert all(probes[n][0]==ids[n] and probes[n][1]>0 for n in product)
init={n for n in re.findall(r"Initializing '([^']+)'",(U/'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not any(n.startswith(t) for t in testPrefixes)};real=init&set(ids);generated=init-set(ids);assert real==set(ci);bindings={}
for n in generated:
 match=re.fullmatch(r'(dev/codex/schubert/nk/api/idempotency/Canonical(?:Field|Request))\$\$Lambda\+0x[0-9a-f]+',n);assert match,n;bindings[n]=match.group(1)
assert collections.Counter(bindings.values())=={'dev/codex/schubert/nk/api/idempotency/CanonicalField':1,'dev/codex/schubert/nk/api/idempotency/CanonicalRequest':2}
rt=ET.parse(U/'coverage.xml').getroot();assert {x.get('name') for x in rt.findall('.//class')}==set(ci);cs={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in rt.findall('counter')};assert all(v['missed']==0 for v in cs.values());assert {k:cs[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=112,METHOD=26,CLASS=4,BRANCH=38)
normal=load(B/'evidence/PG22106-api-stop-static-independent-input-v1/normal.json')['normalPhysicalClassHashes'];unchanged={p:normal['api:'+p]==h for p,h in physical.items()};assert sum(unchanged.values())==3 and all(not unchanged[p] for p in physical if p.endswith(('/CanonicalField.class','/CanonicalRequest.class')))
gold=load(B/'evidence/PG26622-canonical-scalar-fixture-v1/independent-vectors.json');lp=lambda value:len(value).to_bytes(4,'big')+value
for x in gold['vectors']:
 scalar=chr(x['codepoint']);text=('é'+scalar).encode('utf-8');wire=b'SCHUBERT-NK-OP1'+b''.join(lp(v) for v in [b'7',b'QSTREQ01',b'001',('QUESTION:'+scalar).encode('utf-8')])+bytes.fromhex('00000002')+lp(b'text')+lp(b'X1')+lp(text)+lp(b'number')+lp(b'N1')+lp(b'-9223372036854775808');assert wire.hex()==x['canonicalHex'] and hmac.digest(bytes(32),wire,'sha256').hex()==x['hmacSha256']
O.mkdir();files={}
for base,prefix in [(A,'unit-'),(U,'original-')]:
 candidates=[p for p in base.iterdir() if p.is_file()]+list((base/'xml').glob('TEST-*.xml'))
 for p in candidates:
  if p.suffix=='.class':raise AssertionError('Unexpected class at evidence root')
  name='jacoco.exec' if p.name=='jacoco.exec' else prefix+('class-init.stdout' if p.name=='class-init.log' else p.name)
  assert name not in files;shutil.copyfile(p,O/name);files[name]=sha(O/name)
v=dict(actualExit=0,atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),source=source,productionCoreMain=source,run='PG26646-CANONICAL-WHOLE10',tests=10,newDefinitions=2,originalEightPreserved=True,scalarInvalidBoundaryInputs=24,independentValidGoldenVectors=2,redOriginalTests=10,redSuccess=9,redFailed=1,redMalformedBoundaryFailures=24,coverage=cs,physicalClassCount=5,executableClasses=4,positiveMainCrcCount=4,physicalClassHashes=physical,classIds=ids,naturalNoExecutablePackageAnnotation=list(noCode),packageActualJvmMethods=0,jvmGeneratedLambdaOwners=bindings,normalPhysicalUnchanged=unchanged,manualExclusions=[],oldExecCombined=False,inputHashes=b['inputHashes'],dependencies=b['dependencies'],environment=environment,preflightManifest=dict(path=str(pf.relative_to(R)),sha256=sha(pf)),staticApplicable=0,staticRaw=7,processingErrors=0,heldActualClassBinaryIOAndInitAndExternalActions=0,sourceChangedOnlyFactories2=True,formalUpdated=False,newAcceptance=0,whole451Accepted=False,effortRate=None,files=files,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=10,physical=5,coverage=cs,manifestSha256=sha(O/'manifest.json'))))
