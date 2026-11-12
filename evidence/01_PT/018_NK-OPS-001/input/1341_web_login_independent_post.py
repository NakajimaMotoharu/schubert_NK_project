"""Current Web Login162 whole terminal and full197 physical proof, explicit helper deficits retained."""
from pathlib import Path
import collections,datetime,hashlib,json,re,shutil,struct,subprocess,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';W=RUNS/'pg26774-web-login-profile-v1';U=RUNS/'pg26782-web-login-current162-v1';A=B/'evidence/PG26782-web-login-current162-v1';O=B/'evidence/PG26784-web-login-independent-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();m=load(A/'manifest.json');b=m['begin'];assert b['source']=='408c0f1394d4746730b1ab1706b3d182d619caea' and b['productionCoreMain']=='62960fc3b5d4a67cf7bd9df887b668169d10f87f';assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,162,0,0,0)
for p,h in b['inputHashes'].items():assert sha(R/p)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+p])).hexdigest()
for p,h in b['dependencies'].items():assert sha(Path(p))==h
pf=R/b['preflight']['path'];p=load(pf);assert sha(pf)==b['preflight']['sha256'] and p['actualExit']==0 and p['inputHashes']==b['inputHashes'];assert p['staticApplicable']==p['unclassified']==p['processingErrors']==p['checkstyle']==p['spotbugs']==0
for label,v in m['stages'].items():
 assert v['actualExit']==0 and not v['timedOut'] and v==load(A/(label+'-exit.safe.json'))
 for stream in ['stdout','stderr']:assert sha(A/(label+'.'+stream))==v[stream+'Sha256']
cmd=m['stages']['unit']['command'];selected=b['selectedClasses'];assert set(selected)=={v['classname'] for v in b['expectedCases']} and len(selected)==len(set(selected));assert cmd.count('--select-class')==len(selected) and '--select-method' not in cmd and '--scan-classpath' not in cmd;assert not any(x in str(cmd) for x in ['schubert-nk-web-0.1','schubert-nk-api-0.1','schubert-nk-storage','artemis','postgres','enable-native-access','excludes='])
expected={(x['classname'],x['name']) for x in b['expectedCases']};cases=[];env={}
for xml in (U/'xml').glob('TEST-*.xml'):
 rt=ET.parse(xml).getroot();assert not any(rt.findall('.//'+tag) for tag in ['failure','error','skipped']);cases.extend((x.get('classname'),x.get('name')) for x in rt.findall('testcase'));env.update({x.get('name'):x.get('value') for x in rt.findall('./properties/property') if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
assert len(cases)==162 and set(cases)==expected;summary=(A/'unit.stdout').read_text()
for text in ['162 tests found','162 tests started','162 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert text in summary
prepare=load(R/b['prepare']['path']);assert sha(R/b['prepare']['path'])==b['prepare']['sha256'];physical={str(q.relative_to(W/'component')):sha(q) for q in (W/'component').rglob('*.class')};assert physical==b['physicalClassHashes'] and len(physical)==197;assert prepare['wholeWebJarHashedOrOtherPayloadReads'] is False and len(prepare['exactWebEntryPayloadReads'])==9;assert prepare['newTestClassHashes']=={str(q.relative_to(W/'test-classes')):sha(q) for q in (W/'test-classes').rglob('*.class')}
protoTest=load(R/prepare['cachedProtoTest']['path']);ptRoot=RUNS/'pg26304-protocol-unicode-full130-compile-v3/classes';assert protoTest['classHashes']=={str(q.relative_to(ptRoot)):sha(q) for q in ptRoot.rglob('*.class')};loginCompile=load(R/prepare['cachedLoginCompile']['path']);loginTestRoot=RUNS/'pg26524-login-pure-main-subset-v1/test-classes';assert loginCompile['testClassHashes']=={str(q.relative_to(loginTestRoot)):sha(q) for q in loginTestRoot.rglob('*.class')};testNames={n.removesuffix('.class') for n in [*prepare['newTestClassHashes'],*protoTest['classHashes'],*loginCompile['testClassHashes']]}
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(h in n for n in physical for h in held)
def crc64(data):
 value=0
 for byte in data:
  value^=byte
  for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
 return f'{value:016x}'
def code_count(data):
 assert data[:4]==bytes.fromhex('cafebabe');count=struct.unpack_from('>H',data,8)[0];offset=10;i=1;pool={}
 while i<count:
  tag=data[offset];offset+=1
  if tag==1:
   n=struct.unpack_from('>H',data,offset)[0];offset+=2;pool[i]=data[offset:offset+n];offset+=n
  elif tag in [3,4,9,10,11,12,17,18]:offset+=4
  elif tag in [5,6]:offset+=8;i+=1
  elif tag in [7,8,16,19,20]:offset+=2
  elif tag==15:offset+=3
  else:raise AssertionError(tag)
  i+=1
 offset+=6;interfaces=struct.unpack_from('>H',data,offset)[0];offset+=2+2*interfaces;codes=0
 for kind in ['fields','methods']:
  members=struct.unpack_from('>H',data,offset)[0];offset+=2
  for _ in range(members):
   offset+=6;attributes=struct.unpack_from('>H',data,offset)[0];offset+=2
   for _ in range(attributes):
    name,length=struct.unpack_from('>HI',data,offset);offset+=6
    if kind=='methods' and pool[name]==b'Code':codes+=1
    offset+=length
 return codes
ids={n.removesuffix('.class'):crc64((W/'component'/n).read_bytes()) for n in physical};methods={n.removesuffix('.class'):code_count((W/'component'/n).read_bytes()) for n in physical};noCode={n for n,k in methods.items() if k==0};assert len(noCode)==17
protoPost=load(B/'evidence/PG26312-protocol-unicode-full130-independent-v1/manifest.json');switchmaps=set(protoPost['defaultSyntheticSwitchmaps']);assert len(switchmaps)==4 and all(methods[n]>0 for n in switchmaps);assert switchmaps.isdisjoint(noCode)
info={name:dict(crc=crc,instructions=int(inst)) for inst,bran,line,meth,cxty,crc,name in re.findall(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+class 0x([0-9a-f]{16}) (\S+)$',(A/'classinfo.stdout').read_text(),re.M)}
ci={n:v['crc'] for n,v in info.items()};analyzed={n for n,v in info.items() if v['instructions']>0};assert analyzed==set(ids)-noCode-switchmaps and len(analyzed)==176
missing=set(ids)-set(ci);assert len(missing)==10 and all(n.endswith('/package-info') and n in noCode for n in missing);assert len(ci)==187 and all(ids[n]==crc for n,crc in ci.items());zeroInfo=set(ci)-analyzed;assert zeroInfo==(noCode-missing)|switchmaps and len(zeroInfo)==len(noCode-missing)+len(switchmaps)
# Metadata guards reject a missing executable, an unknown entry and a wrong CRC.
assert analyzed-{next(iter(analyzed))} != set(ids)-noCode-switchmaps
assert set(ci)|{'foreign/Unexpected'} != set(ids)-missing
first=next(iter(ci));assert ('0' if ci[first][0]!='0' else '1')+ci[first][1:] != ids[first]
ex=(A/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG26782-WEB-LOGIN-CURRENT162"' in ex;probes={n:(c,int(hit),int(total)) for c,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and n not in testNames};assert observed<=analyzed|switchmaps;assert all(probes[n][0]==ids[n] and probes[n][1]>0 for n in observed)
init={n for n in re.findall(r"Initializing '([^']+)'",(U/'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not any(n==t or n.startswith(t+'$') for t in testNames)};real=init&set(ids);generated=init-set(ids);assert real-noCode==observed
# Hidden adapters are VM-generated, attributed to an exact retained Main owner, never source classes.
def generated_owner(name):
 match=re.fullmatch(r'(dev/codex/schubert/nk/[^+]+)\$\$Lambda\+0x[0-9a-f]+',name)
 return match.group(1) if match and match.group(1) in ids else None
bindings={n:generated_owner(n) for n in generated};assert all(bindings.values())
for foreign in ['dev/codex/schubert/nk/unknown/Foreign$$Lambda+0x12','dev/codex/schubert/nk/protocol/codec/HeaderCodec$$Lambda+bad']:assert generated_owner(foreign) is None
rt=ET.parse(U/'coverage.xml').getroot();assert {x.get('name') for x in rt.findall('.//class')}==set(ci);coverage={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in rt.findall('counter')};assert coverage['CLASS']['covered']+coverage['CLASS']['missed']==176
perClass={node.get('name'):{x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in node.findall('counter')} for node in rt.findall('.//class')};targets={'dev/codex/schubert/nk/web/security/MqAuthenticationProvider','dev/codex/schubert/nk/web/security/MqLoginContextProbe'};assert all(n in perClass for n in targets);targetMisses={n:{k:v for k,v in perClass[n].items() if v['missed']>0} for n in sorted(targets)};helperDeficits={n:{k:v for k,v in counters.items() if v['missed']>0} for n,counters in perClass.items() if n not in targets and any(v['missed']>0 for v in counters.values())};wholeAll100=not any(v['missed'] for v in coverage.values())
for k,v in coverage.items():assert sum(int(x.get('covered')) for cl in rt.findall('.//class') for x in cl.findall('counter') if x.get('type')==k)==v['covered']
# Old9 has exactly three changed Protocol sources; new coverage comes solely from this exec.
assert p['originalEightAssertionsRetained'] and p['finiteOwners']==2 and p['MainChanged'] is False;assert prepare['expectedTests']==162
O.mkdir();files={}
for base,prefix in [(A,'unit-'),(U,'original-')]:
 for q in [x for x in base.iterdir() if x.is_file()]+list((base/'xml').glob('TEST-*.xml')):
  assert q.suffix!='.class';name='jacoco.exec' if q.name=='jacoco.exec' else prefix+('class-init.stdout' if q.name=='class-init.log' else q.name);assert name not in files;shutil.copyfile(q,O/name);files[name]=sha(O/name)
v=dict(actualExit=0,atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),source=b['source'],productionCoreMain=b['productionCoreMain'],run=b['session'],tests=162,originalProvider5AndProbe3Preserved=True,existingProtocol130CombinedSameRun=True,newTestDefinitions=0,wholeSafeFixtures=len(selected),sourceInputs=len(b['inputHashes']),physicalClasses=197,positiveMainCrc=len(observed),executableClasses=176,officialClassinfoMetadataEntries=187,xmlClassEntries=len(rt.findall('.//class')),zeroAnalyzedMetadataEntries=sorted(zeroInfo),naturallyOmittedPackageAnnotations=sorted(missing),coverage=coverage,physicalClassHashes=physical,classIds=ids,actualJvmCodeMethodCounts=methods,naturalNoCodeClasses=sorted(noCode),defaultStandardFilteredSwitchMaps=sorted(switchmaps),hiddenJvmAdapters=bindings,manualCoverageExclusions=[],oldExecCombined=False,preflight=ref(pf),targetCounters={n:perClass[n] for n in sorted(targets)},targetMisses=targetMisses,helperDeficits=helperDeficits,fullClosureFour100=wholeAll100,wholeOwnerFiveAccepted=False,finiteTestOwners2Qualified=True,inputHashes=b['inputHashes'],dependencies=b['dependencies'],environment=env,staticApplicable=0,processingErrors=0,unclassified=0,unchangedWeb9CompileAndStaticReusedWithExactCurrentByte=True,freshWholeTest2Compile=True,oldProtocolCompileAndTestPhysicalBytesReused=True,wholeWebJarOrHeldEntryPayloadReadOrHashed=False,actualDeployedKeysOrBackendOrFourClassAccess=0,originalFilterMock8NotCountedHere=True,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,files=files,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=162,physical=197,positiveCrc=len(observed),coverage=coverage,targetMisses=targetMisses,helperDeficitClasses=len(helperDeficits),manifestSha256=sha(O/'manifest.json'))))
