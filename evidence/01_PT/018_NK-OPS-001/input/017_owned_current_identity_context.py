"""Finite reference-identity review, not runtime PT or a blanket PMD rule waiver."""
from pathlib import Path
import json,hashlib,sys,datetime,subprocess,shutil,importlib.util,collections
ROOT=Path.cwd();RUNS=ROOT.parent/'pgpt-runs/PG379';SLOT=RUNS/'pg19760-f03-identity-context-v1';PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/PG19760-f03-identity-context-v1';RAW=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/PG19744-current-six-main-static-repaired-v1';PRIOR=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/PG19752-f03-finite-source-context-corrected-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
canon=lambda v:json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
GROUPS={
 'RETAINED_REQUEST_OBJECT':([6,13,20,35,42],'Each private Snapshot constructor retains its input request reference; reply validates exactly that same current request and separate primitive owner ID. Content-equal replacement DTO must not grant access to a different capture scope. No crypto/replay/authorization runtime proof.'),
 'THROWABLE_REFERENCE':([76,120,162,184,189,194,196,198,216,221,244,249,253,273,278,306,307,1206,1207,1254,1273,1316,1328,1354,1365,1367,1374,1453,1478,1481],'Throwable catch/parameter references compare by identity before suppression, same-cause duplicate avoidance, or fatal promotion. Throwable.equals can be overridden and cannot identify the identical failure frame; value equality is inappropriate. This review does not certify cleanup ordering, suppressed graph termination, or actual fatal propagation.'),
 'CURRENT_THREAD_IDENTITY':([92,324,381,538,1165,1167,1171,1173,1305,1345,1359,1465],'Compare the actual current Thread object with a captured owner/worker reference. The fields/local owner declarations and currentThread acquisition are preserved as context. A value-equal object is not the executing owner. No thread start/wait/interrupt cleanup/native qualification.'),
 'UNFORGEABLE_OWNER_OR_WITNESS_REFERENCE':([502,504,569,710,711,712,713,714,801,804,807],'Private retained owner/baseline and same actual receipt witness must be the identical object from the current owner cycle. Value equality of state/properties cannot replace this in-memory provenance guard. Static source review only; no actual marker/permit/Unit/Root ownership, retirement, stop, or native proof.'),
 'NESTED_SCOPE_STACK_IDENTITY':([1361],'CURRENT ThreadLocal must hold this exact Scope object before close restores the previous Scope. Equal values from a different nested scope cannot satisfy stack order; no HTTP/log/runtime assembly acceptance.'),
 'SESSION_REPOSITORY_INSTANCE':([1467,1468,1469,1473,1490],'The request marker or saved session owner must be the exact injected SpringEncryptedSessionRepository instance. A different content-equal provider is not the same installed repository authority. Null/mismatch remain failures; no session/auth/key/DB/CSRF runtime qualification.')}

def inspect():
 assert sha(RAW/'manifest.json')=='cef691f454c1324bf16bd01948dbc9f0ed5b2091acb7da5f5817b0a48e9f7d7b'
 assert sha(PRIOR/'manifest.json')=='d4d8274a68727f8bb278ff89140b8778fa5293011263f4e75c8d195e8fe4cf14'
 spec=importlib.util.spec_from_file_location('same_main_static',ROOT/'evidence/01_PT/018_NK-OPS-001/input/014_owned_current_main_static_repaired.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.read_inputs()
 fs=json.loads((RAW/'findings.json').read_text());prior=json.loads((PRIOR/'review.json').read_text());already={r['rawOrdinal'] for r in prior['classified']};mapping={i:(kind,why) for kind,(ids,why) in GROUPS.items() for i in ids};assert len(mapping)==64 and not already.intersection(mapping);assert set(mapping)=={i for i,f in enumerate(fs) if f['rule']=='CompareObjectsWithEquals'}
 rows=[]
 for i in sorted(mapping):
  f=fs[i];p=ROOT/f['path'];assert '/src/main/java/' in f['path'] and sha(p)==f['sourceSha256'];ls=p.read_text().splitlines();n=int(f['attributes']['beginline']);kind,why=mapping[i];context={'firstLine':max(1,n-12),'lastLine':min(len(ls),n+12),'lines':ls[max(0,n-13):min(len(ls),n+12)]};declarations=[{'line':j+1,'text':l} for j,l in enumerate(ls) if any(x in l for x in ['private final Thread','Thread ownerThread =','private final SpringEncryptedSessionRepository','private final BackupStartIntentFiles','private final BackupUnitReceiptGate','private final Baseline','private final UserMutationRequest','private final UserQueryRequest','private final LogRequest','private final QuestionMutationRequest','private final QuestionQueryRequest','this.request =','this.owner =','this.baseline =','ThreadLocal<Scope>'])]
  rows.append({'rawOrdinal':i,'id':f'{i:06d}:'+hashlib.sha256(canon(f)).hexdigest(),'rawFinding':f,'sourceContext':context,'ownerDeclarations':declarations,'reasonCode':kind,'reason':why,'classification':'CONTEXTUAL_NONAPPLICABLE','actualViolation':False,'ptExempt':False,'runtimeProven':False,'newWbsAcceptance':False})
 union=already|set(mapping);assert len(already)==180 and len(union)==244;remaining=[{'rawOrdinal':i,'id':f'{i:06d}:'+hashlib.sha256(canon(f)).hexdigest(),'rawFinding':f,'applicability':'UNCLASSIFIED','actualViolation':None} for i,f in enumerate(fs) if i not in union];assert len(remaining)==1247
 return {'source':'28af318d0198fe7432ca6fcd234d3fabbfd10173','rawManifestSha256':sha(RAW/'manifest.json'),'priorManifestSha256':sha(PRIOR/'manifest.json'),'priorRationaleCorrectionSha256':sha(PRIOR/'rationale-reference-correction.safe.json'),'rawCount':1491,'newContextuallyReviewed':64,'priorContextuallyReviewed':180,'combinedReviewed':244,'remainingCount':1247,'perReasonCounts':dict(collections.Counter(r['reasonCode'] for r in rows)),'classified':rows,'remaining':remaining,'rawGateUnchanged':1,'actualApplicableViolations':None,'wholeF03Accepted':False,'whole451Accepted':False,'productTestsExecuted':0,'coverageMeasured':False,'newWbsAcceptance':0}

def run():
 assert not SLOT.exists() and not PUBLIC.exists();v=inspect();SLOT.mkdir();(SLOT/'review.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');m={'actualExit':0,'atJST':datetime.datetime.now().astimezone().isoformat(),'source':v['source'],'orchestrationHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'driverSha256':sha(__file__),'reviewSha256':sha(SLOT/'review.json'),'counts':v['perReasonCounts'],'newReviewCount':64,'combinedReviewCount':244,'remaining':1247,'newProductProcessCount':0,'productTestsExecuted':0,'coverageMeasured':False,'rawGateUnchanged':1,'fullF03Accepted':False,'formalUpdated':False};(SLOT/'manifest.safe.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({k:m[k] for k in ['actualExit','newReviewCount','combinedReviewCount','remaining']}))

def post():
 m=json.loads((SLOT/'manifest.safe.json').read_text());assert m['actualExit']==0 and m['driverSha256']==sha(__file__) and m['reviewSha256']==sha(SLOT/'review.json');v=inspect();assert v==json.loads((SLOT/'review.json').read_text());fs=json.loads((RAW/'findings.json').read_text());prior=json.loads((PRIOR/'review.json').read_text());allrows=prior['classified']+v['classified']+v['remaining'];by={r['rawOrdinal']:r for r in allrows};assert len(allrows)==len(by)==1491 and set(by)==set(range(1491)) and len({r['id'] for r in allrows})==1491
 for i,f in enumerate(fs):assert by[i]['rawFinding']==f
 for row in v['classified']:
  ls=(ROOT/row['rawFinding']['path']).read_text().splitlines();c=row['sourceContext'];assert c['lines']==ls[c['firstLine']-1:c['lastLine']];assert all(ls[d['line']-1]==d['text'] for d in row['ownerDeclarations'])
 assert not PUBLIC.exists();PUBLIC.mkdir(parents=True)
 for p in SLOT.iterdir():
  if p.is_file():shutil.copyfile(p,PUBLIC/p.name)
 out=dict(m,independentPostReconstruction=True,allOriginalOrdinalsExact=True,disjointPartition1491=True,originalManifestSha256=sha(SLOT/'manifest.safe.json'),files={p.name:sha(p) for p in PUBLIC.iterdir() if p.is_file()});(PUBLIC/'manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'actualExit':0,'manifestSha256':sha(PUBLIC/'manifest.json'),'reviewed':244,'unclassified':1247}))

if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ['run','post']
 if sys.argv[1]=='run':run()
 else:post()
