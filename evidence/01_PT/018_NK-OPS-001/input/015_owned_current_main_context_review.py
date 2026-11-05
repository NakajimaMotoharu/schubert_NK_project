"""Finite Main-only contextual observation review; no Product execution or PT waiver."""
from pathlib import Path
import json,hashlib,sys,re,datetime,subprocess,collections,zipfile,shutil,importlib.util
import xml.etree.ElementTree as E
import pg9666_pagination_static as runner
ROOT=Path.cwd();RUNS=ROOT.parent/'pgpt-runs/PG379';SLOT=RUNS/'pg19750-f03-finite-source-context-v1';PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/PG19750-f03-finite-source-context-v1'
RAW=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/PG19744-current-six-main-static-repaired-v1';RAW_SHA='cef691f454c1324bf16bd01948dbc9f0ed5b2091acb7da5f5817b0a48e9f7d7b'
GSON=ROOT.parent/'toolchain/m2/repository/com/google/code/gson/gson/2.14.0/gson-2.14.0.jar';GSON_SHA='2cbd119bf1961c28788310963dc80ba65f58cdeec1dd139c8bdb1240faa2c36f';JAVAP=ROOT.parent/'toolchain/jdk-25.0.4/bin/javap';PMD=ROOT.parent/'toolchain/static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
canon=lambda v:json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
RARE={
 ('CanonicalField.java','NullAssignment'):'Nullable byte array distinguishes absent canonical value from present empty bytes. Constructor defensively clones present input; changing null to empty changes SS324 framing. OperationFingerprint.writeValue independently branches on null (NULL_LENGTH) versus present length. No NPE contract exemption.',
 ('CanonicalField.java','ReturnEmptyCollectionRatherThanNull'):'The @Nullable accessor preserves the absence sentinel and clones only present bytes. An empty substitute would conflate absence with zero-length canonical field. This is a tagged wire value, not a null collection convenience; no field is dereferenced without guard.',
 ('ResponseSnapshotCodec.java','HardCodedCryptoKey'):'Constructor currentKey is caller-supplied byte[]; validateKey checks nonnull/exact32 and returns key.clone(). The literal currentKey is diagnostic argument name, not key material. No hardcoded secret. Source-only review; actual crypto/key lifecycle and HELD dynamics remain unaccepted.',
 ('ApiReadOnlyObservationAttempt.java','NullAssignment'):'retained is cleared only after owned.close() returns normally. If close throws, exact borrowed Connection/failure frame is retained and unconfirmed is set. Null means no retained ownership; review does not certify actual DB close or fault handling.',
 ('ContinuousConditionWindow.java','NullAssignment'):'Non-VIOLATING state clears previous violation start under the same lock. NORMAL returns zero and UNKNOWN absence; next VIOLATING sample starts a new duration. Nullable state is deliberate reset, with guarded use; actual sampled observation authority remains external.',
 ('InspectorAesCredential.java','NullAssignment'):'Constructor retains owned decoded array; local decoded=null after successful ownership transfer prevents finally zeroing the live owner array. Input/encoded/unmoved decoded remain zeroed in finally. No actual credentials read or executed, and ownership/crypto PT HOLD is not waived.',
 ('SystemManagerObservation.java','NullAssignment'):'finally takes pending into local and clears pending only if nonnull current.closed() confirms closure. A failed/unconfirmed session remains pending. This intentional owner-reference release is not observed native/DBus termination or proof of all close semantics.',
 ('WebHttpServer.java','UseProperClassLoader'):'Embedded Tomcat parent uses the defining WebHttpServer artifact classloader deliberately; ambient thread-context loader could substitute unrelated dependencies. Source packaging/embedded-process design requires fixed artifact identity. No server start/actual runtime classloading acceptance.'}
PEEK={'RequestLogDetails.java','BrokerJournalEvidence.java','ReleaseInventory.java','SessionAttributeCodec.java'}
PATTERNS=[('CURRENT_INTERRUPT_STATUS',r'Thread\.currentThread\(\)\.isInterrupted\(\)','Read current interrupt status; creates no thread and does not clear the flag.'),('CURRENT_THREAD_ID',r'Thread\.currentThread\(\)\.threadId\(\)','Read current thread identity for caller confinement; creates no thread or executor.'),('CURRENT_INTERRUPT_PROPAGATION',r'Thread\.currentThread\(\)\.interrupt\(\)','Preserve/propagate current interrupt status; no thread creation. Does not certify surrounding cleanup, deadline, or external termination.')]

def check_inputs():
 assert sha(RAW/'manifest.json')==RAW_SHA and sha(GSON)==GSON_SHA
 m=json.loads((RAW/'manifest.json').read_text());assert m['actualExit']==0 and m['rawGateExit']==1
 for n,h in m['files'].items():assert sha(RAW/n)==h
 spec=importlib.util.spec_from_file_location('repaired_main_static',ROOT/'evidence/01_PT/018_NK-OPS-001/input/014_owned_current_main_static_repaired.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.read_inputs()
 return m

def reconstruct():
 m=check_inputs();fs=json.loads((RAW/'findings.json').read_text());classified=[];unclassified=[];counts=collections.Counter();seen=set()
 for f in fs:
  assert f['path'].startswith('src/') and '/src/main/java/' in f['path'] and sha(ROOT/f['path'])==f['sourceSha256']
  ident=hashlib.sha256(canon(f)).hexdigest();assert ident not in seen;seen.add(ident);lines=(ROOT/f['path']).read_text().splitlines();n=int(f['attributes']['beginline']);line=lines[n-1];tail=line[int(f['attributes']['begincolumn'])-1:];name=Path(f['path']).name;kind=None;reason=None
  if (name,f['rule']) in RARE:kind='INDIVIDUAL_SOURCE_CONTRACT';reason=RARE[(name,f['rule'])]
  elif name in PEEK and f['rule']=='UnusedReturnValue':
   assert tail.startswith('reader.peek()') and 'reader.setStrictness(Strictness.STRICT);' in '\n'.join(lines) and any('reader.endObject();' in t for t in lines[max(0,n-6):n]);kind='STRICT_TRAILING_DATA_VALIDATION';reason='Pinned Gson2.14 STRICT after root endObject: peek reaches NONEMPTY_DOCUMENT; EOF returns END_DOCUMENT, any extra token checks LENIENT and throws. Ignoring the sole successful enum return preserves the mandatory validating call. Not an unused validation operation. Dependency bytecode proof saved, no Product parser execution.'
  elif f['rule']=='DoNotUseThreads':
   for k,pattern,why in PATTERNS:
    if re.match(pattern,tail):kind=k;reason=why+' PMD rule explicitly targets unmanaged J2EE thread creation. SS311 standalone Java/embedded Web and 411 interrupt discipline apply; no global lifecycle or business behavior waiver.';break
  if kind:
   counts[kind]+=1;classified.append({'id':ident,'rawFinding':f,'sourceContext':{'firstLine':max(1,n-8),'lastLine':min(len(lines),n+8),'lines':lines[max(0,n-9):min(len(lines),n+8)]},'classification':'CONTEXTUAL_NONAPPLICABLE','reasonCode':kind,'reason':reason,'actualViolation':False,'ptExempt':False,'runtimeProven':False,'coverageContribution':None,'newWbsAcceptance':False})
  else:unclassified.append({'id':ident,'rawFinding':f,'applicability':'UNCLASSIFIED','actualViolation':None,'ptExempt':False})
 assert len(fs)==1491 and len(classified)==180 and len(unclassified)==1311 and dict(counts)=={'CURRENT_INTERRUPT_STATUS':100,'CURRENT_INTERRUPT_PROPAGATION':45,'INDIVIDUAL_SOURCE_CONTRACT':8,'CURRENT_THREAD_ID':23,'STRICT_TRAILING_DATA_VALIDATION':4}
 return {'source':m['normalSource'],'rawManifestSha256':RAW_SHA,'rawFindingsSha256':sha(RAW/'findings.json'),'counts':dict(counts),'rawCount':1491,'classifiedCount':180,'unclassifiedCount':1311,'rawGateExitUnchanged':1,'actualApplicableViolationCount':None,'classified':classified,'unclassified':unclassified,'ptExecuted':0,'coverageMeasured':False,'wholeF03Accepted':False,'whole451Accepted':False,'newWbsAcceptance':0}

def excerpts(text):
 # Whole bytecode saved for audit; expose selected control flow only in human review.
 start=text.index('  int doPeek()');end=text.index('\n  private ',start)
 do=text[start:end];at=do.index('     322:') if '     322:' in do else 0
 check=text.index('  private void checkLenient()');checkend=text.index('\n  private ',check+15)
 return {'doPeek':do,'checkLenient':text[check:checkend]}

def run():
 check_inputs();assert not SLOT.exists() and not PUBLIC.exists();SLOT.mkdir();runner.SLOT=SLOT
 with zipfile.ZipFile(PMD) as z:
  rules=E.fromstring(z.read('category/java/multithreading.xml'));rule=next(r for r in rules if r.get('name')=='DoNotUseThreads');raw=E.tostring(rule,encoding='unicode');assert 'J2EE' in raw and 'creates threads' in raw;(SLOT/'thread-rule.xml').write_text(raw+'\n')
 begin={'atJST':datetime.datetime.now().astimezone().isoformat(),'source':'28af318d0198fe7432ca6fcd234d3fabbfd10173','orchestrationHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'driverSha256':sha(__file__),'gsonSha256':sha(GSON),'javapSha256':sha(JAVAP),'pmdJavaJarSha256':sha(PMD),'rawManifestSha256':RAW_SHA,'productClassesExecuted':0,'noRootInvocation':True,'mainOnlyBeforeSourceRead':True};(SLOT/'begin.safe.json').write_text(json.dumps(begin,indent=2)+'\n')
 terminal=runner.step('dependency-javap',[str(JAVAP),'-p','-c','-classpath',str(GSON),'com.google.gson.stream.JsonReader'],SLOT,timeout=30);assert terminal['actualExit']==0 and not terminal['timedOut']
 parts=excerpts((SLOT/'dependency-javap.stdout').read_text());(SLOT/'gson-strict-bytecode.json').write_text(json.dumps(parts,indent=2)+'\n');value=reconstruct();(SLOT/'review.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');m={'actualExit':0,'source':value['source'],'rawCount':1491,'classified':180,'unclassified':1311,'applicabilityStatus':'FINITE_REVIEW_ONLY_NOT_GLOBAL_GATE','atJST':datetime.datetime.now().astimezone().isoformat(),'dependencyTerminal':terminal,'files':{p.name:sha(p) for p in SLOT.iterdir() if p.is_file()},'productTestsExecuted':0,'ptExempt':False,'coverageMeasured':False,'wholeF03Accepted':False,'formalUpdated':False};(SLOT/'manifest.safe.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({k:m[k] for k in ['actualExit','rawCount','classified','unclassified']}))

def post():
 m=json.loads((SLOT/'manifest.safe.json').read_text());b=json.loads((SLOT/'begin.safe.json').read_text());assert m['actualExit']==0 and b['driverSha256']==sha(__file__)
 assert all(sha(SLOT/n)==h for n,h in m['files'].items()) and sha(GSON)==b['gsonSha256'] and sha(JAVAP)==b['javapSha256'] and sha(PMD)==b['pmdJavaJarSha256']
 assert reconstruct()==json.loads((SLOT/'review.json').read_text());assert excerpts((SLOT/'dependency-javap.stdout').read_text())==json.loads((SLOT/'gson-strict-bytecode.json').read_text());t=m['dependencyTerminal'];assert t['actualExit']==0 and t['startUTC']<=t['endUTC'] and not t['timedOut']
 assert not PUBLIC.exists();PUBLIC.mkdir(parents=True)
 for f in SLOT.iterdir():
  if f.is_file():shutil.copyfile(f,PUBLIC/f.name)
 v=dict(m,independentPostReconstruction=True,originalManifestSha256=sha(SLOT/'manifest.safe.json'),files={p.name:sha(p) for p in PUBLIC.iterdir() if p.is_file()});(PUBLIC/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'actualExit':0,'classified':180,'unclassified':1311,'manifestSha256':sha(PUBLIC/'manifest.json')}))

if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ['run','post']
 if sys.argv[1]=='run':run()
 else:post()
