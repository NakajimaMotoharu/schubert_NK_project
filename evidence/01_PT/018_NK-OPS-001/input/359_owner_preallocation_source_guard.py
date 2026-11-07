"""Exact old whole-source inverse and independent finite bookkeeping bound; metadata only, no Process operation."""
from pathlib import Path
import datetime,hashlib,importlib.util,itertools,json
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';OR=B/'evidence/PG23176-owner-preallocation-original-v1';O=B/'evidence/PG23184-owner-preallocation-source-guard-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sp=importlib.util.spec_from_file_location('tokens',R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py');lib=importlib.util.module_from_spec(sp);sp.loader.exec_module(lib);tok=lib.java_tokens

def replace(t,a,z):
 a=tok(a);z=tok(z);matches=[i for i in range(len(t)) if t[i:i+len(a)]==a];assert len(matches)==1,(a,len(matches));i=matches[0];return t[:i]+z+t[i+len(a):]
def inverse_caller(source):
 t=tok(source);prefix=tok('new OwnedTestProcess(');positions=[i for i in range(len(t)) if t[i:i+len(prefix)]==prefix]
 for i in reversed(positions):
  start=i+len(prefix);depth=1;j=start
  while depth:
   depth+=(t[j]=='(')-(t[j]==')');j+=1
  argument=t[start:j-1];assert argument and argument[-4:]!=tok('.start()');t[j-1:j-1]=tok('.start()')
 return t,len(positions)
def inverse_helper(source):
 t=tok(source);t=replace(t,'// At most six failure records along any cleanup branch; reserve two additional slots.\n private final List<Throwable> cleanupFailures=new ArrayList<>(8); private final IOException terminalUnknown=new IOException("owned test child terminal state unknown");','')
 t=replace(t,'OwnedTestProcess(ProcessBuilder builder)throws IOException{// Instance state is ready before the final acquisition; no caller starts an unprepared owner.\n this.ownedChild=Objects.requireNonNull(builder,"owned test builder").start();}','OwnedTestProcess(Process process){this.ownedChild=Objects.requireNonNull(process,"owned test child");}')
 t=replace(t,'var failures=cleanupFailures;','var failures=new ArrayList<Throwable>();');t=replace(t,'failures.add(terminalUnknown);','failures.add(new IOException("owned test child terminal state unknown"));');return t
def helper_contract(s):
 t=tok(s)
 def has(text):
  a=tok(text);return any(t[i:i+len(a)]==a for i in range(len(t)-len(a)+1))
 return all(has(v) for v in ['private final List<Throwable> cleanupFailures=new ArrayList<>(8);','private final IOException terminalUnknown=new IOException("owned test child terminal state unknown");','OwnedTestProcess(ProcessBuilder builder)throws IOException{','this.ownedChild=Objects.requireNonNull(builder,"owned test builder").start();','var failures=cleanupFailures;','failures.add(terminalUnknown);','if(closeAttempted)return;closeAttempted=true;']) and s.count('.start()')==1 and 'new ArrayList' not in s[s.index('public void close()'):s.index('private boolean awaitExit()')]
def main():
 assert not O.exists();m=json.loads((OR/'manifest.json').read_bytes());rows=[];neg=[];owners=0
 for v in m['inputs']:
  p=R/v['path'];old=OR/v['backup'];assert sha(old)==v['sha256'];source=p.read_text()
  if p.name=='OwnedTestProcess.java':
   assert inverse_helper(source)==tok(old.read_text()) and helper_contract(source)
   for a,z in [('new ArrayList<>(8)','new ArrayList<>(5)'),('var failures = cleanupFailures;','var failures = new ArrayList<Throwable>();'),('Objects.requireNonNull(builder, "owned test builder").start()','Objects.requireNonNull(builder, "owned test builder").startPipeline()')]:
    assert a in source and not helper_contract(source.replace(a,z,1));neg.append(dict(path=v['path'],mutation=a))
  else:
   inverse,count=inverse_caller(source);assert inverse==tok(old.read_text());owners+=count
   # Leaving an acquisition at a caller is rejected, even when the old normal oracle is identical.
   a='new OwnedTestProcess(';i=source.index(a)+len(a);bad=source[:i]+'null'+source[i:]
   try:valid=inverse_caller(bad)[0]==tok(old.read_text())
   except (AssertionError,IndexError):valid=False
   assert not valid;neg.append(dict(path=v['path'],mutation='extra constructor argument token'))
  rows.append(dict(path=v['path'],sha256=sha(p),originalSha256=v['sha256'],allOtherTokensPreserved=True))
 assert owners==8
 # Independent abstract-path enumeration from the four optional failed operations and final branch.
 counts=[]
 for termFailed,firstWait,forceFailed,secondWait,streamFails in itertools.product([0,1],['error','alive','terminated'],[0,1],['error','alive','terminated'],range(4)):
  first=termFailed+(firstWait=='error')
  counts.append(first+streamFails if firstWait=='terminated' else first+forceFailed+((secondWait=='error')+1 if secondWait!='terminated' else streamFails))
 assert max(counts)==6<8;O.mkdir();value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputs=rows,callerOwnerSites=8,independentMaximumFailureRecords=max(counts),reservedCapacity=8,abstractPaths=len(counts),metadataNegativeGuards=neg,originalTestsCompiled=0,productTestsExecuted=0,actualProductProcessActions=0,ptPassCount=None,coverage=None,sourceFixStatus='CLEANUP_BOOKKEEPING_PREPARED_BEFORE_ACQUISITION_SOURCE_ONLY',bugs=['BUG-2477'],ykts=['YKT-2215']);(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print('old six whole-source inverse0/eight callers/record max6 capacity8/eight metadata negatives; no Product execution')
if __name__=='__main__':main()
