"""Original async child/executor source ownership corrections only; original native Tests stay HOLD."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';F=B/'evidence/PG22940-storage-async-ownership-original-v1';G=B/'evidence/PG22942-storage-async-ownership-guard-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());T='src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/';NAMES=['OwnedTransferDirectoryTest.java','LinuxStartupAdmissionTest.java']
def one(t,a,b):assert t.count(a)==1,(a,t.count(a));return t.replace(a,b,1)
def transform(name,text):
 method='bug036CallerMonitorCannotBlockAnyDirectoryOperation' if name=='OwnedTransferDirectoryTest.java' else 'childfd007ConcurrentReadyAndOuterCleanupConsumeAExactlyOnce';a=text.index('void '+method+'(');z=text.index('\n  @Test',a);part=text[a:z]
 if name=='OwnedTransferDirectoryTest.java':
  part=one(part,'OwnedTransferDirectory child;\n      synchronized (parent) {\n        child = executor.submit(() -> parent.openDate(DATE)).get(5, TimeUnit.SECONDS);','synchronized (parent) {\n        assertEquals(\n            Boolean.TRUE,\n            executor.submit(() -> {\n              try (var opened = parent.openDate(DATE)) {\n                return opened.atDirectory(path -> Files.isDirectory(path));\n              }\n            }).get(5, TimeUnit.SECONDS));');part=one(part,'synchronized (child) {','try (var child = parent.openExistingDate(DATE); executor) {\n      synchronized (child) {');part=one(part,'.get(5, TimeUnit.SECONDS);\n      }\n    }\n    assertTrue(calls.live.isEmpty());','.get(5, TimeUnit.SECONDS);\n      }\n      }\n    }\n    assertTrue(calls.live.isEmpty());')
 else:
  assert name=='LinuxStartupAdmissionTest.java';part=one(part,'var executor = Executors.newFixedThreadPool(8);\n    try {','try (var executor = Executors.newFixedThreadPool(8)) {\n    try {');part=one(part,'executor.shutdownNow();\n    }\n    assertEquals(List.of(P, A), f.closed);','executor.shutdownNow();\n    }\n    }\n    assertEquals(List.of(P, A), f.closed);')
 return text[:a]+part+text[z:]
def main():
 phase=sys.argv[1];assert phase in ['apply','guard']
 if phase=='apply':
  assert not F.exists();s=importlib.util.spec_from_file_location('storage84_freeze',B/'input/296_storage_current84.py');lib=importlib.util.module_from_spec(s);s.loader.exec_module(lib);base,raw,h,reviews=lib.current();planned={n:transform(n,(R/(T+n)).read_text()) for n in NAMES};F.mkdir();inputs=[]
  for name in NAMES:
   p=R/(T+name);snap=F/name;snap.write_bytes(p.read_bytes());inputs.append(dict(path=T+name,sha256=sha(p),snapshotPath=str(snap.relative_to(R))))
  m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputs=inputs,currentInputHashes=h,allCurrentRaw=raw,reviewedFindings=reviews,baseline=base,productTestsExecuted=0,originalTestsCompiled=False);(F/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
  for item in inputs:
   p=R/item['path'];assert sha(p)==item['sha256'];p.write_text(planned[p.name])
  print('original2 frozen; async acquisition owns close and executor cancellation precedes owner close');return
 assert not G.exists();m=load(F/'manifest.json');s=importlib.util.spec_from_file_location('async_ownership_tokens',R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py');lib=importlib.util.module_from_spec(s);s.loader.exec_module(lib);tok=lib.java_tokens;negative=0
 for item in m['inputs']:
  old=R/item['snapshotPath'];assert sha(old)==item['sha256'];expected=transform(old.name,old.read_text());actual=(R/item['path']).read_text();assert tok(actual)==tok(expected);markers=['try (var opened = parent.openDate(DATE))','try (var child = parent.openExistingDate(DATE); executor)'] if old.name=='OwnedTransferDirectoryTest.java' else ['try (var executor = Executors.newFixedThreadPool(8))','executor.shutdownNow();']
  for marker in markers:assert marker in actual;assert tok(actual.replace(marker,'BROKEN_OWNER',1))!=tok(expected);negative+=1
 G.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),originalManifest=dict(path=str((F/'manifest.json').relative_to(R)),sha256=sha(F/'manifest.json')),currentHashes={v['path']:sha(R/v['path']) for v in m['inputs']},correctedOwnershipSites=2,metadataNegativeGuards=negative,productTestsExecuted=0,originalTestsCompiled=False);(G/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sourceSites=2,negative=negative)))
if __name__=='__main__':main()
