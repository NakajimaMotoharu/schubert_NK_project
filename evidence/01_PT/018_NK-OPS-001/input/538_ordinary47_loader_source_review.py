"""Bind original loader diagnostics to current ordinary Test source as data; never load it."""
from pathlib import Path
from collections import Counter
import datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
from public_catch_manual_lexer import lexical
R=Path(__file__).resolve().parents[4]; B=R/'evidence/01_PT/018_NK-OPS-001'
C=B/'input/537_ordinary47_loader_scope.json'; O=B/'evidence/PG23822-ordinary47-loader-source-review-v1'
load=lambda p:json.loads(p.read_bytes()); sha=lambda raw:hashlib.sha256(raw).hexdigest()
cfg=load(C)

def calls(text):
 t=lexical(text); words=[v for v,_ in t]; result=[]
 def close(at):
  pairs={'(':')','[':']','{':'}'};stack=[]
  for i in range(at,len(words)):
   w=words[i]
   if w in pairs:stack.append(pairs[w])
   elif w in (')',']','}'):
    assert stack and stack.pop()==w
    if not stack:return i
  raise ValueError('complete balanced invocation required')
 for at in range(len(words)-3):
  if words[at:at+4]!=['Proxy','.','newProxyInstance','(']:continue
  stop=close(at+3); start=at+4; args=[]; i=start
  while i<stop:
   if words[i] in ('(','[','{'):i=close(i)+1;continue
   if words[i]==',':args.append((start,i));start=i+1
   i+=1
  args.append((start,stop));assert len(args)==3 and all(a<z for a,z in args)
  a,z=args[0]; first=words[a:z]
  assert first[-4:]==['.','getClassLoader','(',')']
  owner=first[:-4]; assert len(owner) in (1,3) and re.fullmatch(r'[A-Za-z_$][\w$]*',owner[0])
  if len(owner)==3:assert owner[1:]==['.','class']
  a2,z2=args[1]; interfaces=words[a2:z2]
  assert interfaces[:2]==['new','Class'] and '[' in interfaces and '{' in interfaces and interfaces[-1]=='}'
  assert 'LITERAL' not in first+interfaces and 'getContextClassLoader' not in first
  # Signature deliberately excludes handler bodies and their literals. No raw fixture data emitted.
  category='TYPE_DEFINING_LOADER' if len(owner)==1 or owner[0] in interfaces else 'OWN_TEST_DEFINING_LOADER'
  result.append(dict(begin=t[at][1],end=t[stop][1]+1,loaderBegin=t[a][1],loaderEnd=t[z-1][1]+1,loader=''.join(first),interfaceDeclaration=''.join(interfaces),category=category))
 assert sum(w=='getClassLoader' for w in words)==len(result)
 return result

assert not O.exists(); p=R/cfg['originalManifest']['path']; assert sha(p.read_bytes())==cfg['originalManifest']['sha256']
old=load(p); p=R/cfg['originalPmd']['path']; assert sha(p.read_bytes())==cfg['originalPmd']['sha256']
raw=[]
for f in E.parse(p).getroot():
 if f.tag.rsplit('}',1)[-1]!='file':continue
 name=str(Path(f.get('name')).relative_to(R))
 for v in f:
  if v.get('rule')==cfg['rule']:raw.append((name,dict(v.attrib)))
assert len(raw)==93 and {n for n,_ in raw}==set(cfg['currentSourcePins'])
reviews=[]; inventory={}; changed=0
for name,pin in cfg['currentSourcePins'].items():
 assert re.fullmatch(r'src/schubert-nk-(api|batch|web)/src/test/java/[A-Za-z0-9_/$]+\.java',name)
 assert not any(v in name for v in ('RootFailedStart','SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness'))
 current=(R/name).read_bytes(); assert sha(current)==pin
 previous=subprocess.check_output(['git','show',cfg['originalSource']+':'+name],cwd=R)
 assert sha(previous)==cfg['originalSourcePins'][name]==old['begin']['inputHashes'][name]
 a=previous.decode();z=current.decode();before=calls(a);after=calls(z)
 signature=lambda row:(row['loader'],row['interfaceDeclaration'],row['category'])
 assert [signature(v) for v in before]==[signature(v) for v in after]
 changed+=sha(previous)!=pin
 inventory[name]=dict(originalSha256=sha(previous),currentSha256=pin,sourceBytesEqual=previous==current,loaderCalls=len(before),orderedCallSignaturesUnchanged=True)
 lines=a.splitlines(keepends=True); currentLines=z.splitlines(keepends=True); used=[]
 for _,v in [row for row in raw if row[0]==name]:
  start=sum(map(len,lines[:int(v['beginline'])-1]))+int(v['begincolumn'])-1
  end=sum(map(len,lines[:int(v['endline'])-1]))+int(v['endcolumn'])
  found=[i for i,c in enumerate(before) if start<=c['loaderBegin']<c['loaderEnd']<=end]
  assert len(found)==1; i=found[0]; used.append(i);n=after[i]
  reviews.append(dict(path=name,originalSourceSha256=sha(previous),currentSourceSha256=pin,rawDiagnostic=v,rawDiagnosticOrdinalInSource=len(used)-1,originalInvocation=before[i],currentInvocation=n,currentLine=z.count('\n',0,n['loaderBegin'])+1,disposition='SOURCE_CONTEXT_NOT_J2EE_TEST_PROXY_DEFINING_LOADER',reason='The loader is the interface/type defining loader, or the own Test defining loader for its explicitly visible Proxy interfaces. This ordinary standalone JUnit source is not a J2EE/container. Thread context loader replacement is not required by that rule in this context. Visibility is a source contract here, not a new runtime measurement.',rawPreserved=True,productTestsExecuted=0,coverageMeasured=False))
 assert Counter(used)==Counter(range(len(before)))
assert len(reviews)==93 and len(inventory)==47
O.mkdir(); (O/'review.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n')
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['originalSource'],observerHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),config=dict(path=str(C.relative_to(R)),sha256=sha(C.read_bytes())),originalManifest=cfg['originalManifest'],originalPmd=cfg['originalPmd'],originalDiagnosticCount=93,sourceFiles=47,currentChangedSources=changed,currentOrderedLoaderCallSignaturesIdentical=True,sourceInventory=inventory,reviewSha256=sha((O/'review.json').read_bytes()),sourceContextDispositionCounts=dict(Counter(v['currentInvocation']['category'] for v in reviews)),rawRuleSuppressed=False,other254OriginalDiagnosticsIndividuallyUnchangedOrReconciled=False,currentWholeStaticMeasurement=False,currentWholeUnknownCount=None,priorTwentyFixtureOverlapCredit=None,newCompilerOrJvmExecutions=0,productTestsExecuted=0,productClassesInitialized=0,actualBackendActions=0,heldFourInitializations=0,originalProducerOrScannerExecuted=False,newAcceptance=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__).read_bytes())))
(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,sites=93,files=47,changed=changed,categories=value['sourceContextDispositionCounts'],manifestSha256=sha((O/'manifest.json').read_bytes()))))
