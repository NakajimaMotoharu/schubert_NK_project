"""Independent raw-character lexer and exact typed-field/current-public-byte validation."""
from pathlib import Path
from collections import Counter
import datetime,json,hashlib,re,copy
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001/evidence';S=B/'PG23534-g07-normalized-catch-provenance-v1';O=B/'PG23536-g07-normalized-catch-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');key=lambda x:tuple(x[n] for n in ['path','ruleId','startLine','endLine','inputSha256'])
def lexical(text):
 out=[];i=0
 while i<len(text):
  at=i;c=text[i]
  if c.isspace():i+=1;continue
  if text.startswith('//',i):
   z=text.find('\n',i+2);i=len(text) if z<0 else z;continue
  if text.startswith('/*',i):
   z=text.find('*/',i+2);assert z>=0;i=z+2;continue
  if c in ['"',"'"]:
   if text.startswith('"""',i):
    z=text.find('"""',i+3);assert z>=0;i=z+3
   else:
    quote=c;i+=1
    while i<len(text) and text[i]!=quote:
     i+=2 if text[i]=='\\' else 1
    assert i<len(text);i+=1
   out.append(('LITERAL',at));continue
  if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$':
   i+=1
   while i<len(text) and text[i] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$0123456789':i+=1
   out.append((text[at:i],at));continue
  out.append((c,at));i+=1
 return out

def bodies(text):
 tokens=lexical(text);out=[]
 def closing(at,left,right):
  assert tokens[at][0]==left;depth=0
  for j in range(at,len(tokens)):
   if tokens[j][0]==left:depth+=1
   elif tokens[j][0]==right:depth-=1
   if depth==0:return j
  raise AssertionError('incomplete declared raw-source delimiter')
 for at,(word,offset) in enumerate(tokens):
  if word!='catch':continue
  end=closing(at+1,'(',')');head=[x for x,_ in tokens[at+2:end]]
  if 'SQLException' not in head:continue
  stop=closing(end+1,'{','}');body=[x for x,_ in tokens[end+2:stop]];out.append((text.count('\n',0,offset)+1,hashlib.sha256(json.dumps(body).encode()).hexdigest()))
 return out
# Tool-only lexical oracle checks; they neither invoke nor count any Production test.
golden='try { f(); } catch (SQLException failure) { /* comment */ log("literal"); throw failure; }';expected=hashlib.sha256(json.dumps(['log','(','LITERAL',')',';','throw','failure',';']).encode()).hexdigest();assert bodies(golden)==[(1,expected)]
assert bodies('// catch(SQLException e) { hidden(); }\nString a="catch(SQLException e) {hidden();}";')==[]
assert bodies("catch (RuntimeException failure) { throw failure; }")==[]
assert lexical("'\\\'' \"escaped \\\" text\" // eof")==[('LITERAL',0),('LITERAL',5)]
assert not O.exists();m=load(S/'manifest.json');assert sha(S/'manifest.json')=='400554c6e643a4cd8ae7cc65a0d88573e5f0c1033d8cb4fc64476fbea9be801d';assert m['actualExit']==0;assert sha(R/m['tool']['path'])==m['tool']['sha256'];cfg=load(R/m['config']['path']);assert sha(R/m['config']['path'])==m['config']['sha256'];allowed=set(cfg['allowedSources']);assert len(allowed)==40 and set(m['sourcePins'])==set(m['sourceGitBlobs'])==allowed
normal=R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==m['normalManifestSha256'];nm=load(normal);assert nm['source']==m['normalCoreSource']==cfg['normalSource'];proofs={};counts={}
for name in sorted(allowed):
 assert name.startswith(('src/schubert-nk-api/src/main/java/','src/schubert-nk-web/src/main/java/')) and not any(v in name.lower() for v in cfg['denyTokens']);p=R/name;assert not p.is_symlink() and p.resolve()==p;raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==m['sourcePins'][name]==nm['begin']['inputHashes'][name];assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==m['sourceGitBlobs'][name]
 items=bodies(raw.decode());counts[name]=len(items)
 for line,value in items:proofs.setdefault(value,set()).add((name,line))
assert counts==m['currentPublicCatchCounts']
originalp=R/m['originalMetadata']['path'];assert sha(originalp)==m['originalMetadata']['sha256'];rows=load(originalp);original=Counter(map(key,rows));assert len(rows)==4493;old=[]
for ref in m['priorUpdateRefs']:
 p=R/ref['path'];assert sha(p)==ref['sha256'];old+=load(p)
previous=Counter(map(key,old));assert len(old)==11 and sum((original-previous).values())==4482
p=R/m['input']['path'];assert sha(p)==m['input']['sha256']==cfg['artifactSha256'];text=p.read_text();sites=load(p);assert len(sites)==113;selected=[v for v in rows if v['path']==m['input']['path'] and not previous[key(v)]];assert len(selected)==73
# Separate pretty-object indexing, rather than producer raw_decode span arithmetic.
idx=-1;fields={};lines=text.splitlines()
for line_no,line in enumerate(lines,1):
 if line=='  {':idx+=1
 if line.strip().startswith('"bodyTokenSha256":'):fields[line_no]=sites[idx]
assert idx+1==113 and len(fields)==113
updates=load(S/'updates.json');retained=load(S/'retained.json');assert sha(S/'updates.json')==m['updatesSha256'] and sha(S/'retained.json')==m['retainedSha256'];assert updates==[] and len(retained)==73 and Counter(map(key,selected))==Counter(map(key,retained));by={key(v):v for v in retained}
for v in selected:
 assert v['startLine']==v['endLine'] and v['startLine'] in fields;obj=fields[v['startLine']];line=lines[v['startLine']-1];literal=re.fullmatch(r'\s+"bodyTokenSha256": "([a-f0-9]{64})",?',line);assert literal and literal[1]==obj['bodyTokenSha256']
 if obj['sourcePath'] not in allowed:assert by[key(v)]['status']=='ORIGINAL_SOURCE_OUTSIDE_READ_SET'
 else:assert literal[1] not in proofs and by[key(v)]['status']=='NO_PUBLIC_TOKEN_TRANSFORM_WITNESS'
assert m['newFalsePositives']==0 and m['remainingUnclassified']==4482 and m['historicalWholeFileSourceIdentityUnqualifiedUpdates']==0
# Never accept a display-only shape, invented classification, or old-source success transfer.
def contract(v):
 assert v['newFalsePositives']==0 and v['remainingUnclassified']==4482 and v['actualSecretCount'] is None and v['binaryOrContainerLimited']==22 and v['productTestsExecuted']==v['actualAuthOrDbActions']==v['heldFourInitializations']==v['newAcceptance']==0 and all(v[k] is False for k in ['scannerExecuted','operatorMainExecuted','targetsExecuted','privateRawRead','historyExpanded','capturedValuesWritten','captureValueHashesWritten','wholeG07Accepted','whole451Accepted'])
contract(m)
for k,value in [('newFalsePositives',1),('remainingUnclassified',4481),('actualSecretCount',0),('binaryOrContainerLimited',0),('actualAuthOrDbActions',1),('heldFourInitializations',1),('wholeG07Accepted',True),('productTestsExecuted',1)]:
 wrong=copy.deepcopy(m);wrong[k]=value
 try:contract(wrong)
 except AssertionError:pass
 else:raise AssertionError('unproven boundary claim accepted')
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifest=dict(path=str((S/'manifest.json').relative_to(R)),sha256=sha(S/'manifest.json')),independentLexing='RAW_CHARACTER_SCANNER_SEPARATE_FROM_PRODUCER_REGEX',lexicalOracleChecks=4,sourcePins=m['sourcePins'],currentPublicSources=40,currentPublicSqlCatchCount=sum(counts.values()),candidateRows=73,positiveCaptureMatches=0,newFalsePositives=0,remainingUnclassified=4482,actualSecretCount=None,binaryOrContainerLimited=22,metadataNegativeChecks=8,productTestsExecuted=0,scannerExecuted=False,privateRawRead=False,targetsExecuted=False,actualAuthOrDbActions=0,heldFourInitializations=0,capturedValuesWritten=False,captureValueHashesWritten=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,classified=0,remaining=4482,publicCatches=sum(counts.values()),manifestSha256=sha(O/'manifest.json'))))
