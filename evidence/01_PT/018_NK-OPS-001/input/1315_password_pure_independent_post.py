"""Whole original6 genuine terminal, current3 physical and independent password oracles; no rerun."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,struct,subprocess,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';W=RUNS/'pg26700-password-pure-profile-v1';U=RUNS/'pg26710-password-whole6-v1';A=B/'evidence/PG26710-password-whole6-v1';O=B/'evidence/PG26712-password-pure-independent-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();m=load(A/'manifest.json');b=m['begin'];assert b['source']=='33c6baa2d65bc9b0ea779d16336c6b82c9511262' and b['productionCoreMain']=='62960fc3b5d4a67cf7bd9df887b668169d10f87f';assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,6,0,0,0)
for p,h in b['inputHashes'].items():assert sha(R/p)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+p])).hexdigest()
for p,h in b['dependencies'].items():assert sha(Path(p))==h
pf=R/b['preflight']['path'];fm=load(pf);assert fm['actualExit']==0 and sha(pf)==b['preflight']['sha256'] and fm['inputHashes']==b['inputHashes'];assert all(fm[k]==0 for k in ['staticApplicable','processingErrors','unclassified','checkstyle','spotbugs']);assert fm['MainOrTestChanged'] is False
for label,v in m['stages'].items():
 assert v['actualExit']==0 and not v['timedOut'] and v==load(A/(label+'-exit.safe.json'))
 for stream in ['stdout','stderr']:assert sha(A/(label+'.'+stream))==v[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==2 and '--select-method' not in cmd and '--scan-classpath' not in cmd;assert not any(x in str(cmd) for x in ['schubert-nk-api-0.1','schubert-nk-web-0.1','schubert-nk-storage','artemis','postgres','enable-native-access','excludes='])
expected={(x['classname'],x['name']) for x in b['expectedCases']};actual=[];env={}
for xml in (U/'xml').glob('TEST-*.xml'):
 rt=ET.parse(xml).getroot();assert not any(rt.findall('.//'+x) for x in ['failure','error','skipped']);actual.extend((t.get('classname'),t.get('name')) for t in rt.findall('testcase'));env.update({x.get('name'):x.get('value') for x in rt.findall('./properties/property') if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
assert len(actual)==6 and set(actual)==expected
for text in ['6 tests found','6 tests started','6 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert text in (A/'unit.stdout').read_text()
prepare=load(R/b['prepare']['path']);assert sha(R/b['prepare']['path'])==b['prepare']['sha256'];assert prepare['wholeApiJarHashedOrOtherEntryPayloadReads'] is False;physical={str(p.relative_to(W/'main')):sha(p) for p in (W/'main').rglob('*.class')};assert physical==b['physicalClassHashes'] and len(physical)==3;assert prepare['testClassHashes']=={str(p.relative_to(W/'test-classes')):sha(p) for p in (W/'test-classes').rglob('*.class')}
def crc64(data):
 v=0
 for byte in data:
  v^=byte
  for _ in range(8):v=(v>>1)^0xd800000000000000 if v&1 else v>>1
 return f'{v:016x}'
ids={n.removesuffix('.class'):crc64((W/'main'/n).read_bytes()) for n in physical};package={n for n in ids if n.endswith('/package-info')};assert len(package)==1;ci={n:c for c,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(A/'classinfo.stdout').read_text())};assert set(ci)==set(ids)-package and len(ci)==2 and all(ids[n]==c for n,c in ci.items())
# Read only own allowed package annotation class; actual JVM method_count0, not a scope exclusion.
data=(W/'main'/(next(iter(package))+'.class')).read_bytes();assert data[:4]==bytes.fromhex('cafebabe');cp=struct.unpack_from('>H',data,8)[0];offset=10;i=1
while i<cp:
 tag=data[offset];offset+=1
 if tag==1:n=struct.unpack_from('>H',data,offset)[0];offset+=2+n
 elif tag in [3,4,9,10,11,12,17,18]:offset+=4
 elif tag in [5,6]:offset+=8;i+=1
 elif tag in [7,8,16,19,20]:offset+=2
 elif tag==15:offset+=3
 else:raise AssertionError(tag)
 i+=1
offset+=6;n=struct.unpack_from('>H',data,offset)[0];offset+=2+2*n;assert struct.unpack_from('>HH',data,offset)==(0,0)
ex=(A/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG26710-PASSWORD-WHOLE6"' in ex;probes={n:(c,int(hit),int(total)) for c,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};testNames={n.removesuffix('.class') for n in prepare['testClassHashes']};observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and n not in testNames};assert observed==set(ci) and all(probes[n][0]==ids[n] and probes[n][1]>0 for n in observed)
init={n for n in re.findall(r"Initializing '([^']+)'",(U/'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not any(n==t or n.startswith(t+'$') for t in testNames)};assert init&set(ids)==observed;generated=init-set(ids);bindings={}
for n in generated:
 match=re.fullmatch(r'(dev/codex/schubert/nk/api/security/PasswordPolicy)\$\$Lambda\+0x[0-9a-f]+',n);assert match,n;bindings[n]=match.group(1)
assert len(bindings)==1
rt=ET.parse(U/'coverage.xml').getroot();assert {c.get('name') for c in rt.findall('.//class')}==set(ci);coverage={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in rt.findall('counter')};assert all(v['missed']==0 for v in coverage.values());assert {k:coverage[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=44,METHOD=10,CLASS=2,BRANCH=22)
# Independent fixed vector supplementary to the original JCA Test; never invokes product code.
import hashlib as independent_hash
salt=bytes(range(16));vector='{pbkdf2-v1}'+salt.hex()+independent_hash.pbkdf2_hmac('sha256',('é'*12).encode('utf-8'),salt,310000,32).hex();assert len(vector)==107 and len(vector.removeprefix('{pbkdf2-v1}'))==96
O.mkdir();files={}
for base,prefix in [(A,'unit-'),(U,'original-')]:
 for p in [q for q in base.iterdir() if q.is_file()]+list((base/'xml').glob('TEST-*.xml')):
  assert p.suffix!='.class';name='jacoco.exec' if p.name=='jacoco.exec' else prefix+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,O/name);files[name]=sha(O/name)
v=dict(actualExit=0,atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),source=b['source'],productionCoreMain=b['productionCoreMain'],run=b['session'],tests=6,newDefinitions=0,wholeOriginalFixtures=2,physicalClasses=3,executableClasses=2,positiveMainCrc=2,coverage=coverage,physicalClassHashes=physical,classIds=ids,naturalNoCodePackageAnnotation=list(package),actualPackageJvmMethods=0,hiddenJvmAdapterOwners=bindings,manualExclusions=[],oldExecCombined=False,preflight=ref(pf),inputHashes=b['inputHashes'],dependencies=b['dependencies'],environment=env,staticApplicable=0,processingErrors=0,unclassified=0,format=0,checkstyle=0,spotbugs=0,publicSyntheticPbkdf2AdditionalVector=dict(purpose='Public independent audit data, no deployed credential',saltHex=salt.hex(),iterations=310000,derivedBits=256,independentExpectedVector=vector,usedAsNewProductTest=False),existingSurrogateNegativeProofForGlobalYkt2328Index13=True,globalRemainingOtherTargetsNotClosed=True,originalGroupEstimateRetained=True,addedBudget=0,actualCredentialKeyAuthSessionDbBackendAndHeldClassIO=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,files=files,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=6,physical=3,coverage=coverage,manifestSha256=sha(O/'manifest.json'))))
