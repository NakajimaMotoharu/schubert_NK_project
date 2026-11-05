"""Source-only finite Resource exception type-dispatch review; no resource or Product use."""
from pathlib import Path
import json,hashlib,sys,datetime,subprocess,shutil,importlib.util,collections
ROOT=Path.cwd();RUNS=ROOT.parent/'pgpt-runs/PG379';SLOT=RUNS/'pg19830-resource-type-context-v1';PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/PG19830-resource-type-context-v1';BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence';RAW=BASE/'PG19744-current-six-main-static-repaired-v1';PRIORS=[('PG19752-f03-finite-source-context-corrected-v1','d4d8274a68727f8bb278ff89140b8778fa5293011263f4e75c8d195e8fe4cf14'),('PG19760-f03-identity-context-v1','40e501ddd751e8e7849721e7a063d69062d49ad3ba0e1e3429c345b5245723bf'),('PG19770-f03-map-monitor-context-v1','6a272d4a9ecad5c26ee13e3af9765f766f9fcd2936ec1e0b39bf030a8778bae4')];NAMES={'ResourceScope.java':10,'ProcessResourceScope.java':20,'ConfigurationGroupResolver.java':8};sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();canon=lambda v:json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()

def inspect():
 assert sha(RAW/'manifest.json')=='cef691f454c1324bf16bd01948dbc9f0ed5b2091acb7da5f5817b0a48e9f7d7b';spec=importlib.util.spec_from_file_location('current_static_normal',ROOT/'evidence/01_PT/018_NK-OPS-001/input/014_owned_current_main_static_repaired.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.read_inputs();refs=[]
 for num,nums in [('333',[17,27,29,33]),('343',[785,787,789])]:
  paths=list((ROOT/'documents/300_SS').glob('*/'+num+'*'));assert len(paths)==1;p=paths[0];b=subprocess.check_output(['git','show','origin/main:'+str(p.relative_to(ROOT))]);assert hashlib.sha256(b).hexdigest()==sha(p);ls=b.decode().splitlines()
  for n in nums:refs.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'line':n,'text':ls[n-1]})
 previous=[]
 for name,h in PRIORS:
  p=BASE/name;assert sha(p/'manifest.json')==h;previous+=json.loads((p/'review.json').read_text())['classified']
 old={r['rawOrdinal'] for r in previous};assert len(previous)==len(old)==269;fs=json.loads((RAW/'findings.json').read_text());rows=[];counts=collections.Counter()
 for i,f in enumerate(fs):
  name=Path(f['path']).name
  if f['rule']!='AvoidInstanceofChecksInCatchClause' or name not in NAMES:continue
  assert i not in old and sha(ROOT/f['path'])==f['sourceSha256'];ls=(ROOT/f['path']).read_text().splitlines();n=int(f['attributes']['beginline']);method=f['attributes'].get('method');line=ls[n-1].strip()
  if name=='ResourceScope.java':
   assert method in ['acquire','use'];kind='IO_OWNER_COMPOUND_DISPATCH';why='SS333 lines27/29 defines one same-owner cleanup attempt before deciding known IOException versus unknown Runtime/Error and fixed redacted secondary. The inspected primary/secondary type tests implement that cross-product; the outer StorageIoException test keeps original reason only with no suppressed failure. Separate catch clauses cannot inspect the simultaneously retained opposite failure without duplicating this mandated matrix. This accepts this syntax purpose only, not actual close/ownership/unknown-body runtime behavior.'
  elif name=='ProcessResourceScope.java':
   assert method in ['acquire','use'];kind='STOP_IO_INTERRUPT_COMPOUND_DISPATCH';why='SS333 line33/SS343 line787 explicitly groups known IO/Interrupted/StopGate primary against unknown cleanup and preserves current interrupt before throwing unknown cleanup. Unknown primary is retained with a new fixed Stop secondary, avoiding raw/self suppression. The tests after the same one-time cleanup are the design type table, not business exception flow. No process/stdio close or stop result is established by this review.'
  else:
   assert method in ['scope','readResult']
   if method=='scope':kind='CHECKED_LOOKUP_COMPOUND_DISPATCH';why='SS343 line785 requires IO/Interrupted versus unchecked cleanup, interrupt preservation and fixed IOException secondary with unknown original primary. The local checked scope deliberately differs from StopGate helper; narrowing all catches to StopGate would change the approved public exception contract. Current source preserves same release attempt and raw unknown identity; no NSS lookup or process/reader termination is run.'
   else:kind='ASYNC_CAUSE_UNWRAP';why='The catch is ExecutionException from Future.get, while inspected values are its retained nonnull cause. A catch(IOException) or catch(RuntimeException) on get would not catch the wrapped failure. The owned Callable invokes only read(InputStream,byte[]): declared IOException, unchecked RuntimeException or Error. SS343 line785 explicitly mandates fixed diagnostics for IO/Runtime and Error identity. This source proof neither runs a Future nor certifies provider/process completion.'
  counts[name]+=1;rows.append({'rawOrdinal':i,'id':f'{i:06d}:'+hashlib.sha256(canon(f)).hexdigest(),'rawFinding':f,'sourceContext':{'firstLine':max(1,n-12),'lastLine':min(len(ls),n+12),'lines':ls[max(0,n-13):min(len(ls),n+12)]},'reasonCode':kind,'reason':why,'method':method,'observedLine':line,'classification':'CONTEXTUAL_NONAPPLICABLE','actualViolation':False,'ptExempt':False,'runtimeProven':False,'newWbsAcceptance':False})
 assert dict(counts)==NAMES and len(rows)==38;selected=old|{r['rawOrdinal'] for r in rows};assert len(selected)==307;rest=[{'rawOrdinal':i,'id':f'{i:06d}:'+hashlib.sha256(canon(f)).hexdigest(),'rawFinding':f,'applicability':'UNCLASSIFIED','actualViolation':None} for i,f in enumerate(fs) if i not in selected];assert len(rest)==1184
 return {'source':'28af318d0198fe7432ca6fcd234d3fabbfd10173','rawCount':1491,'newContext':38,'priorContext':269,'combinedReviewed':307,'remainingCount':1184,'classified':rows,'remaining':rest,'canonicalMain':subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),'canonicalDesignReferences':refs,'rawGateUnchanged':1,'actualApplicableViolations':None,'productExecuted':False,'coverageMeasured':False,'newAcceptance':0,'wholeF03Accepted':False,'whole451Accepted':False}

def run():
 assert not SLOT.exists() and not PUBLIC.exists();v=inspect();SLOT.mkdir();(SLOT/'review.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');m={'actualExit':0,'source':v['source'],'atJST':datetime.datetime.now().astimezone().isoformat(),'driverSha256':sha(__file__),'reviewSha256':sha(SLOT/'review.json'),'orchestrationHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'newContext':38,'combinedReviewed':307,'remaining':1184,'productExecuted':False,'newAcceptance':0,'wholeF03Accepted':False};(SLOT/'manifest.safe.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'actualExit':0,'context':38,'combined':307,'unclassified':1184}))

def post():
 m=json.loads((SLOT/'manifest.safe.json').read_text());assert m['actualExit']==0 and m['driverSha256']==sha(__file__) and m['reviewSha256']==sha(SLOT/'review.json');v=inspect();assert v==json.loads((SLOT/'review.json').read_text());allrows=[]
 for name,h in PRIORS:allrows+=json.loads((BASE/name/'review.json').read_text())['classified']
 allrows+=v['classified']+v['remaining'];by={r['rawOrdinal']:r for r in allrows};assert len(allrows)==len(by)==1491 and set(by)==set(range(1491)) and len({r['id'] for r in allrows})==1491
 for i,f in enumerate(json.loads((RAW/'findings.json').read_text())):assert by[i]['rawFinding']==f
 for r in v['classified']:
  ls=(ROOT/r['rawFinding']['path']).read_text().splitlines();c=r['sourceContext'];assert c['lines']==ls[c['firstLine']-1:c['lastLine']]
 assert not PUBLIC.exists();PUBLIC.mkdir(parents=True)
 for p in SLOT.iterdir():
  if p.is_file():shutil.copyfile(p,PUBLIC/p.name)
 out=dict(m,independentPostReconstruction=True,allOriginalOrdinalsExact=True,disjointPartition1491=True,originalManifestSha256=sha(SLOT/'manifest.safe.json'),files={p.name:sha(p) for p in PUBLIC.iterdir() if p.is_file()});(PUBLIC/'manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'actualExit':0,'manifestSha256':sha(PUBLIC/'manifest.json'),'combined':307,'remaining':1184}))

if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ['run','post']
 if sys.argv[1]=='run':run()
 else:post()
