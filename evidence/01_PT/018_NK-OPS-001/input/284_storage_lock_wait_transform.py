"""Three exact source corrections; no original Test compile/run or native operation."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';F=B/'evidence/PG22884-storage-lock-wait-original-v1';G=B/'evidence/PG22886-storage-lock-wait-guard-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());T='src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/'
NAMES=['ChildDirectoryPublicationTest.java','LinuxStartupAdmissionTest.java','PrivateChildDirectoryTest.java']
# Exact replacements are independent of expected values and Main implementation.
def replacement(name,text):
 edits=[]
 if name=='PrivateChildDirectoryTest.java':
  edits=[('import java.util.concurrent.TimeUnit;','import java.util.concurrent.TimeUnit;\nimport java.util.concurrent.locks.ReentrantLock;'),('final Set<Integer> live = ConcurrentHashMap.newKeySet();','final Set<Integer> live = ConcurrentHashMap.newKeySet();\n    private final ReentrantLock liveLock = new ReentrantLock();'),('synchronized (live) {','liveLock.lock();\n                    try {'),('return result;\n                    }\n                  });','return result;\n                    } finally {\n                      liveLock.unlock();\n                    }\n                  });')]
 elif name=='ChildDirectoryPublicationTest.java':edits=[('import java.util.concurrent.Future;','import java.util.concurrent.Future;\nimport java.util.concurrent.TimeUnit;'),('if (result.get()) successes++;','if (result.get(10, TimeUnit.SECONDS)) successes++;')]
 else:
  assert name=='LinuxStartupAdmissionTest.java';edits=[('import java.util.concurrent.ExecutionException;','import java.util.concurrent.ExecutionException;\nimport java.util.concurrent.TimeUnit;'),('executor.invokeAll(jobs)','executor.invokeAll(jobs, 10, TimeUnit.SECONDS)')]
 for a,b in edits:assert text.count(a)==1,(name,a);text=text.replace(a,b,1)
 return text,edits

def main():
 phase=sys.argv[1];assert phase in ['apply','guard']
 if phase=='apply':
  assert not F.exists();h=B/'input/280_storage_current89.py';s=importlib.util.spec_from_file_location('freeze_storage89',h);lib=importlib.util.module_from_spec(s);s.loader.exec_module(lib);baseline,raw,hashes,previous=lib.current();review=B/'evidence/PG22868-storage-map-sync-independent-v1/manifest.json';assert sha(review)=='c17ee0373867f3555792397375f602554e30f80f327e844317b53ae4b9782ce1';rm=load(review);assert rm['inputHashes']==hashes;inputs=[];planned={name:replacement(name,(R/(T+name)).read_text()) for name in NAMES};F.mkdir();edits={}
  for name in NAMES:
   n=T+name;p=R/n;before=p.read_text();after,e=planned[name];snap=F/name;snap.write_bytes(p.read_bytes());inputs.append(dict(path=n,sha256=sha(p),snapshotPath=str(snap.relative_to(R))));edits[n]=e
  m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputs=inputs,currentInputHashes=hashes,allCurrentRaw=raw,reviewedFindings=rm['previousReviewed']+rm['reviewedFindings'],baseline=baseline,reviewManifest=dict(path=str(review.relative_to(R)),sha256=sha(review)),edits=edits,productTestsExecuted=0,originalTestsCompiled=False);(F/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
  for item in inputs:
   p=R/item['path'];assert sha(p)==item['sha256'];p.write_text(replacement(p.name,p.read_text())[0])
  print('original3 frozen; private lock1 and finite wait2 source-fixed only');return
 assert not G.exists();m=load(F/'manifest.json');lex=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';s=importlib.util.spec_from_file_location('lock_wait_tokens',lex);lib=importlib.util.module_from_spec(s);s.loader.exec_module(lib);tok=lib.java_tokens;neg=0
 for i in m['inputs']:
  old=(R/i['snapshotPath']).read_text();assert sha(R/i['snapshotPath'])==i['sha256'];expected,edits=replacement(Path(i['path']).name,old);actual=(R/i['path']).read_text();assert tok(expected)==tok(actual)
  for marker,bad in ([('liveLock.unlock();','liveLock.lock();'),('liveLock.lock();\n                    try {','try {')] if Path(i['path']).name=='PrivateChildDirectoryTest.java' else [('10, TimeUnit.SECONDS','0, TimeUnit.SECONDS')]):
   altered=actual.replace(marker,bad,1);assert tok(altered)!=tok(expected);neg+=1
 G.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),originalManifest=dict(path=str((F/'manifest.json').relative_to(R)),sha256=sha(F/'manifest.json')),currentHashes={i['path']:sha(R/i['path']) for i in m['inputs']},otherTokensFixturesAndExpectedValuesUnchanged=True,privateMonitorCorrections=1,finiteWaitCorrections=2,negativeGuards=neg,productTestsExecuted=0,originalTestsCompiled=False);(G/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,changedFiles=3,negative=neg)))
if __name__=='__main__':main()
