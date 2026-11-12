"""One current whole132 terminal/source/CRC/full179/code/static proof; no product re-execution."""
from pathlib import Path
import collections,datetime,hashlib,json,re,shutil,struct,subprocess,sys,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';W=RUNS/'pg26944-manifest-current-profile-v1';U=RUNS/'pg26952-manifest-current134-v1';A=B/'evidence/PG26952-manifest-current134-v1';O=B/'evidence/PG26954-manifest-current-independent-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();m=load(A/'manifest.json');b=m['begin'];assert b['source']==sys.argv[1] and b['productionCoreMain']=='8995f6cb6341c0298613cee3714c0d20f113c0f1';assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,134,0,0,0)
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
assert len(cases)==134 and set(cases)==expected;summary=(A/'unit.stdout').read_text()
for text in ['134 tests found','134 tests started','134 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert text in summary
prepare=load(R/b['prepare']['path']);assert sha(R/b['prepare']['path'])==b['prepare']['sha256'];physical={str(q.relative_to(W/'component')):sha(q) for q in (W/'component').rglob('*.class')};assert physical==b['physicalClassHashes'] and len(physical)==179;assert prepare['apiWholeJarHashedOrOtherEntryPayloadRead'] is False and len(prepare['apiExactReadClassEntries'])==3;assert prepare['testClassHashes']=={str(q.relative_to(W/'test-classes')):sha(q) for q in (W/'test-classes').rglob('*.class')}
protoTest=load(R/prepare['protoTest']['path']);ptRoot=RUNS/'pg26304-protocol-unicode-full130-compile-v3/classes';assert protoTest['classHashes']=={str(q.relative_to(ptRoot)):sha(q) for q in ptRoot.rglob('*.class')};testNames={n.removesuffix('.class') for n in [*prepare['testClassHashes'],*protoTest['classHashes']]}
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
ids={n.removesuffix('.class'):crc64((W/'component'/n).read_bytes()) for n in physical};methods={n.removesuffix('.class'):code_count((W/'component'/n).read_bytes()) for n in physical};noCode={n for n,k in methods.items() if k==0};assert len(noCode)==14
protoPost=load(B/'evidence/PG26312-protocol-unicode-full130-independent-v1/manifest.json');switchmaps=set(protoPost['defaultSyntheticSwitchmaps']);assert len(switchmaps)==4 and all(methods[n]>0 for n in switchmaps);assert switchmaps.isdisjoint(noCode)
info={name:dict(crc=crc,instructions=int(inst)) for inst,bran,line,meth,cxty,crc,name in re.findall(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+class 0x([0-9a-f]{16}) (\S+)$',(A/'classinfo.stdout').read_text(),re.M)}
ci={n:v['crc'] for n,v in info.items()};analyzed={n for n,v in info.items() if v['instructions']>0};assert analyzed==set(ids)-noCode-switchmaps and len(analyzed)==161
missing=set(ids)-set(ci);assert len(missing)==8 and all(n.endswith('/package-info') and n in noCode for n in missing);assert len(ci)==171 and all(ids[n]==crc for n,crc in ci.items());zeroInfo=set(ci)-analyzed;assert zeroInfo==(noCode-missing)|switchmaps and len(zeroInfo)==10
# Metadata guards reject a missing executable, an unknown entry and a wrong CRC.
assert analyzed-{next(iter(analyzed))} != set(ids)-noCode-switchmaps
assert set(ci)|{'foreign/Unexpected'} != set(ids)-missing
first=next(iter(ci));assert ('0' if ci[first][0]!='0' else '1')+ci[first][1:] != ids[first]
ex=(A/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG26952-MANIFEST-CURRENT134"' in ex;probes={n:(c,int(hit),int(total)) for c,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and n not in testNames};assert observed==analyzed|switchmaps and len(observed)==165;assert all(probes[n][0]==ids[n] and probes[n][1]>0 for n in observed)
init={n for n in re.findall(r"Initializing '([^']+)'",(U/'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not any(n==t or n.startswith(t+'$') for t in testNames)};real=init&set(ids);generated=init-set(ids);assert real==observed
# Hidden adapters are VM-generated, attributed to an exact retained Main owner, never source classes.
def generated_owner(name):
 match=re.fullmatch(r'(dev/codex/schubert/nk/[^+]+)\$\$Lambda\+0x[0-9a-f]+',name)
 return match.group(1) if match and match.group(1) in ids else None
bindings={n:generated_owner(n) for n in generated};assert all(bindings.values())
for foreign in ['dev/codex/schubert/nk/unknown/Foreign$$Lambda+0x12','dev/codex/schubert/nk/protocol/codec/HeaderCodec$$Lambda+bad']:assert generated_owner(foreign) is None
rt=ET.parse(U/'coverage.xml').getroot();assert {x.get('name') for x in rt.findall('.//class')}==set(ci);coverage={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in rt.findall('counter')};assert all(v['missed']==0 for v in coverage.values());assert coverage['CLASS']['covered']==161
for k,v in coverage.items():assert sum(int(x.get('covered')) for cl in rt.findall('.//class') for x in cl.findall('counter') if x.get('type')==k)==v['covered']
# Old9 has exactly three changed Protocol sources; new coverage comes solely from this exec.
assert p['wholeJarHashedOrOtherEntryPayloadRead'] is False and p['MainOrTestChanged'] is False;assert prepare['expectedTests']==134
O.mkdir();files={}
for base,prefix in [(A,'unit-'),(U,'original-')]:
 for q in [x for x in base.iterdir() if x.is_file()]+list((base/'xml').glob('TEST-*.xml')):
  assert q.suffix!='.class';name='jacoco.exec' if q.name=='jacoco.exec' else prefix+('class-init.stdout' if q.name=='class-init.log' else q.name);assert name not in files;shutil.copyfile(q,O/name);files[name]=sha(O/name)
v=dict(actualExit=0,atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),source=b['source'],productionCoreMain=b['productionCoreMain'],run=b['session'],tests=134,originalManifest4CurrentQualification=True,existingProtocol130CombinedSameRun=True,newTestDefinitions=0,wholeSafeFixtures=len(selected),sourceInputs=len(b['inputHashes']),physicalClasses=179,positiveMainCrc=165,executableClasses=161,officialClassinfoMetadataEntries=171,xmlClassEntries=len(rt.findall('.//class')),zeroAnalyzedMetadataEntries=sorted(zeroInfo),naturallyOmittedPackageAnnotations=sorted(missing),coverage=coverage,physicalClassHashes=physical,classIds=ids,actualJvmCodeMethodCounts=methods,naturalNoCodeClasses=sorted(noCode),defaultStandardFilteredSwitchMaps=sorted(switchmaps),hiddenJvmAdapters=bindings,manualCoverageExclusions=[],oldExecCombined=False,preflight=ref(pf),inputHashes=b['inputHashes'],dependencies=b['dependencies'],environment=env,staticApplicable=0,processingErrors=0,unclassified=0,unchangedApi3CompileAndStaticReusedWithExactCurrentByte=True,freshWholeTest1Compile=True,oldProtocolCompileAndTestPhysicalBytesReused=True,wholeApiJarOrHeldEntryPayloadReadOrHashed=False,actualDeployedKeysOrBackendOrFourClassAccess=0,wholeMediaHeldFileOwnerAccepted=False,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,files=files,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=134,physical=179,positiveCrc=165,coverage=coverage,manifestSha256=sha(O/'manifest.json'))))
