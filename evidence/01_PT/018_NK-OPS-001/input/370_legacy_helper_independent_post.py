"""Independent source declaration/path/classfile-name post; passive binary reads, no class loading."""
from pathlib import Path
import datetime,hashlib,json,re,struct,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';P=B/'evidence/PG23208-legacy-helper-output-binding-v1/manifest.json';O=B/'evidence/PG23210-legacy-helper-independent-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();v=json.loads(P.read_text());assert v['actualExit']==0 and v['helpersConsidered']==27 and v['sourceCurrent']==v['outerOutputsPresent']==25 and v['originalBinaryIdentityQualified']==0
snapshot=R.parent/'pgpt-runs/PG379/pg10024-test-hygiene-six-compile-v1/snapshot'
blocked=('RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest','SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness','FingerprintKeyRing','ResponseSnapshotCodec','TemporaryInfrastructureException','WebStartupException')
def class_name(data):
 assert data[:4]==bytes.fromhex('cafebabe') and int.from_bytes(data[6:8],'big')==69
 count=int.from_bytes(data[8:10],'big');i=1;pos=10;pool={}
 while i<count:
  tag=data[pos];pos+=1
  if tag==1:
   n=int.from_bytes(data[pos:pos+2],'big');pos+=2;pool[i]=data[pos:pos+n];pos+=n
  elif tag in (7,8,16,19,20):pool[i]=int.from_bytes(data[pos:pos+2],'big');pos+=2
  elif tag in (3,4,9,10,11,12,17,18):pos+=4
  elif tag in (5,6):pos+=8;i+=1
  elif tag==15:pos+=3
  else:raise AssertionError('unsupported constant tag')
  i+=1
 this=int.from_bytes(data[pos+2:pos+4],'big');return pool[pool[this]].decode('ascii')
def safe_output(p):
 assert p.is_relative_to(snapshot) and '/target/test-classes/' in str(p)
 assert not any(s in str(p) for s in blocked)
 assert all(not x.is_symlink() for x in (p,*p.parents))
 assert p.is_file();return p
rows=[];binaries=0
for item in v['helpers']:
 s=item['helper'];assert s.startswith('src/') and '/src/test/java/' in s and not any(w in s for w in blocked);p=R/s;text=p.read_text();assert sha(p)==item['currentSourceSha256'];package=re.search(r'(?m)^package\s+([\w.]+);',text).group(1);fqn=package+'.'+p.stem;assert fqn==item['declaredFqn'];assert item['originalClassDigestAvailable'] is False and item['originalCompileTimeBinaryIdentityProven'] is False
 if not item['sourcePinCurrent']:
  assert item['compilerInputSourceHash']!=sha(p) and 'observedOuterSha256' not in item;rows.append(dict(helper=s,status='SAVED_COMPILER_SOURCE_STALE_OUTPUT_NOT_READ'));continue
 assert item['compilerInputSourceHash']==sha(p);cp=safe_output(Path(item['candidateOutput']));assert sha(cp)==item['observedOuterSha256'];name=class_name(cp.read_bytes());assert name==fqn.replace('.','/');binaries+=1
 for nested in item['nestedObservedFiles']:
  np=safe_output(cp.with_name(nested['name']));assert sha(np)==nested['sha256'];assert class_name(np.read_bytes()).startswith(name+'$');binaries+=1
 rows.append(dict(helper=s,sourcePinCurrent=True,passiveOuterName=name,observedNested=len(item['nestedObservedFiles']),originalBinaryIdentityQualified=False))
assert binaries==50 and len(rows)==27
neg=0
sample=next(x for x in v['helpers'] if x['sourcePinCurrent']);data=Path(sample['candidateOutput']).read_bytes()
for bad in (b'NOPE'+data[4:],data[:6]+b'\x00\x01'+data[8:]):
 try:class_name(bad)
 except (AssertionError,IndexError,KeyError):neg+=1
 else:raise AssertionError('bad binary accepted')
assert class_name(data)!='example/WrongHelper';neg+=1
assert sample['originalCompileTimeBinaryIdentityProven'] is False;neg+=1
assert not O.exists();O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),primaryManifest=dict(path=str(P.relative_to(R)),sha256=sha(P)),helpers=rows,helpersConsidered=27,currentSourceSavedOuterOutputObserved=25,sourceStaleOutputNotRead=2,passiveClassNamesVerified=binaries,originalCompileBinaryIdentityProven=0,metadataNegativeChecks=neg,originalTestsCompiled=0,productTestsExecuted=0,productClassesInitialized=0,actualProductProcessActions=0,newSourceProofs=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,outer25=True,stale2NotRead=True,binaryNames=binaries,originalBinaryIdentityQualified=0,negative=neg,manifestSha256=sha(O/'manifest.json'))))
