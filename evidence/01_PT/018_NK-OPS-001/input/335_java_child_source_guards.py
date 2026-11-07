"""Source-only exact old-oracle comparison and process-owner contract negatives; no Product invocation."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,re
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';D=R/'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage';O=B/'evidence/PG23108-java-child-source-guards-v2';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sp=importlib.util.spec_from_file_location('oldtoken',R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py');lib=importlib.util.module_from_spec(sp);sp.loader.exec_module(lib);tok=lib.java_tokens

def replace_once(tokens,a,z):
 a=tok(a);z=tok(z);matches=[i for i in range(len(tokens)) if tokens[i:i+len(a)]==a];assert len(matches)==1,(a,len(matches));i=matches[0];return tokens[:i]+z+tokens[i+len(a):]
def inverse(source,name):
 t=tok(source)
 if name=='LinuxProcessExecTest.java':
  t=replace_once(t,'try(var childOwner=new OwnedTestProcess(builder.start())){var child=childOwner.process();','var child=builder.start();try{')
  # The original finally belongs only to this last Test, immediately before the next method comment.
  comment='// Every pointed string is freshly allocated by the tested confined arena; bounded fixture only.'
  t=replace_once(t,'assertEquals(-1,child.getInputStream().read());}}'+comment,'assertEquals(-1,child.getInputStream().read());}finally{if(child.isAlive())child.destroy();}}'+comment)
 else:
  a=tok('try(var executor=Executors.newSingleThreadExecutor();var childOwner=new OwnedTestProcess(');i=next(i for i in range(len(t)) if t[i:i+len(a)]==a);j=next(j for j in range(i+len(a),len(t)) if t[j:j+len(tok(')){var child=childOwner.process();'))]==tok(')){var child=childOwner.process();'));builder=t[i+len(a):j];oldPrefix=tok('var child=')+builder+tok(';try(var executor=Executors.newSingleThreadExecutor();var reader=child.inputReader()){');newEnd=j+len(tok(')){var child=childOwner.process();try(var reader=child.inputReader()){'));assert t[j:newEnd]==tok(')){var child=childOwner.process();try(var reader=child.inputReader()){');t=t[:i]+oldPrefix+t[newEnd:]
  t=replace_once(t,'finally{childOwner.close();}}}}private static LinuxExecDescriptors fixture','finally{if(child.isAlive())child.destroy();}}}private static LinuxExecDescriptors fixture')
 return t

def owner_contract(s):
 t=tok(s)
 def has(x):
  a=tok(x);return any(t[i:i+len(a)]==a for i in range(len(t)-len(a)+1))
 return all(has(x) for x in ['private static final long WAIT_NANOS=TimeUnit.SECONDS.toNanos(5);','if(closeAttempted)return;closeAttempted=true;interrupted=Thread.interrupted();','ownedChild.destroy();','ownedChild.destroyForcibly();','terminated=awaitExit();','if(terminated){closeStream(ownedChild.getOutputStream(),failures);closeStream(ownedChild.getInputStream(),failures);closeStream(ownedChild.getErrorStream(),failures);}','failures.add(new IOException("owned test child terminal state unknown"));','finally{if(interrupted)Thread.currentThread().interrupt();}','long started=System.nanoTime();','long remaining=WAIT_NANOS-(System.nanoTime()-started);','if(remaining<=0)return !ownedChild.isAlive();','if(ownedChild.waitFor(remaining,TimeUnit.NANOSECONDS))return true;','if(!reaches(selected,secondary)&&!reaches(secondary,selected))selected.addSuppressed(secondary);','if(!seen.add(current))continue;']) and s.count('terminated = awaitExit();')==2 and not any(x in t for x in ['ProcessBuilder','ProcessHandle','descendants']) and 'ownedChild.waitFor()' not in s
def main():
 assert not O.exists();original=json.loads((B/'evidence/PG23092-java-child-owner-original-v1/manifest.json').read_bytes());rows=[];neg=[]
 for v in original['inputs']:
  p=R/v['path'];old=B/'evidence/PG23092-java-child-owner-original-v1'/v['backup'];assert sha(old)==v['sha256'];s=p.read_text();assert inverse(s,p.name)==tok(old.read_text());rows.append(dict(path=v['path'],oldSha256=v['sha256'],sha256=sha(p),allOtherOracleArgvAndMethodTokensPreserved=True))
  changed=s.replace('childOwner.process()','childOwner.process().toHandle()',1)
  try:valid=inverse(changed,p.name)==tok(old.read_text())
  except (AssertionError,StopIteration):valid=False
  assert not valid;neg.append(p.name+':owner accessor')
 helper=D/'OwnedTestProcess.java';s=helper.read_text();assert owner_contract(s)
 for a,z in [('toNanos(5)','toNanos(50)'),('closeAttempted = true','closeAttempted = false'),('WAIT_NANOS - (System.nanoTime() - started)','WAIT_NANOS'),('ownedChild.waitFor(remaining, TimeUnit.NANOSECONDS)','ownedChild.waitFor()'),('if (interrupted) Thread.currentThread().interrupt();','Thread.interrupted();'),('ownedChild.destroyForcibly();','ownedChild.destroy();')]:
  assert a in s;assert not owner_contract(s.replace(a,z,1));neg.append(a)
 O.mkdir();value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputs=rows,helper=dict(path=str(helper.relative_to(R)),sha256=sha(helper)),metadataNegativeGuards=neg,scope='SOURCE_ONLY_TWO_JAVA_PARENTS_NOT_FORK_CHILDREN_OR_RUNTIME_PROOF',originalTestsCompiled=False,productTestsExecuted=0,processActions=0,actualPass=None,coverage=None,bugs=['BUG-2467'],ykts=['YKT-2205'],remainingParentSites=6,forkSitesUnchanged=5);(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print('two original whole source inverse0/helper eight metadata negatives0; original Test compile/run0')
if __name__=='__main__':main()
