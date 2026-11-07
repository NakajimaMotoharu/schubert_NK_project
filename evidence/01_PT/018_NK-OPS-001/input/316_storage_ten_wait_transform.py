"""Ten exact original native-related Test waits source-only; original runtime remains HOLD."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';F=B/'evidence/PG23006-storage-ten-wait-original-v1';G=B/'evidence/PG23008-storage-ten-wait-guard-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());T='src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/'
CFG={'LinuxExecDescriptorsTest.java':('executor.invokeAll(work)',1),'LinuxHostDirectoryCallsTest.java':('executor.invokeAll(work)',1),'LinuxInodeSecurityTest.java':('pool.invokeAll(tasks)',1),'LinuxProcessExecTest.java':('executor.invokeAll(work)',1),'LinuxDirectoryCallsTest.java':('executor.invokeAll(tasks)',2),'LinuxSealedProofTest.java':('executor.invokeAll(work)',1),'LinuxFileLockTest.java':('executor.invokeAll(work)',1),'LinuxStartupFileLockTest.java':('executor.invokeAll(work)',1),'ServiceConfigFilesTest.java':('job.get()',1)}
def transform(name,text):
 old,count=CFG[name];assert text.count(old)==count;new=old[:-1]+(', 30, TimeUnit.SECONDS)' if 'invokeAll' in old else '10, TimeUnit.SECONDS)');text=text.replace(old,new)
 if 'import java.util.concurrent.TimeUnit;' not in text:assert text.count('import java.util.concurrent.Executors;')==1;text=text.replace('import java.util.concurrent.Executors;','import java.util.concurrent.Executors;\nimport java.util.concurrent.TimeUnit;')
 return text

def main():
 phase=sys.argv[1];assert phase in ['apply','guard']
 if phase=='apply':
  assert not F.exists();p=B/'evidence/PG23002-storage-thread46-independent-v1/manifest.json';assert sha(p)=='d04fc6bf75e7de862a7a6356dac9ca6be38193e2b40a3e5d36bb33552ded23dc';m=load(p);assert m['actualExit']==0;c=m['currentStorage29'];assert len(c['currentInputHashes'])==29 and len(c['allCurrentRaw'])==len(c['reviewedFindings'])==82
  for n,h in c['currentInputHashes'].items():assert n.startswith('src/schubert-nk-storage/src/test/java/') and not any(x in n for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']) and sha(R/n)==h
  planned={name:transform(name,(R/(T+name)).read_text()) for name in CFG};F.mkdir();inputs=[]
  for name in CFG:
   p=R/(T+name);snap=F/name;snap.write_bytes(p.read_bytes());inputs.append(dict(path=T+name,sha256=sha(p),snapshotPath=str(snap.relative_to(R)),waitSites=CFG[name][1],addedTimeUnitImport='import java.util.concurrent.TimeUnit;' not in p.read_text()))
  v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputs=inputs,currentStorage29=c,baseline=dict(path=str((B/'evidence/PG23002-storage-thread46-independent-v1/manifest.json').relative_to(R)),sha256=sha(B/'evidence/PG23002-storage-thread46-independent-v1/manifest.json')),productTestsExecuted=0,originalTestsCompiled=False);(F/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
  for item in inputs:
   p=R/item['path'];assert sha(p)==item['sha256'];p.write_text(planned[p.name])
  print('original9 frozen; bulk9 deadline30SECONDS and submitted Future1 deadline10SECONDS source-only');return
 assert not G.exists();m=load(F/'manifest.json');sp=importlib.util.spec_from_file_location('storage_ten_wait_tokens',R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py');lib=importlib.util.module_from_spec(sp);sp.loader.exec_module(lib);tok=lib.java_tokens;negative=0
 for item in m['inputs']:
  p=R/item['path'];old=R/item['snapshotPath'];assert sha(old)==item['sha256'];want=transform(p.name,old.read_text());actual=p.read_text();assert tok(want)==tok(actual);deadline='10, TimeUnit.SECONDS' if p.name=='ServiceConfigFilesTest.java' else '30, TimeUnit.SECONDS'
  for z in ['0, TimeUnit.SECONDS',deadline.replace('SECONDS','MINUTES')]:assert tok(actual.replace(deadline,z,1))!=tok(want);negative+=1
 G.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),originalManifest=dict(path=str((F/'manifest.json').relative_to(R)),sha256=sha(F/'manifest.json')),currentHashes={i['path']:sha(R/i['path']) for i in m['inputs']},finiteWaitCorrections=10,bulkDeadlines=9,submittedFutureDeadlines=1,metadataNegativeGuards=negative,allOtherJavaTokensFixturesAndOraclesUnchanged=True,productTestsExecuted=0,originalTestsCompiled=False);(G/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,changedSources=9,finiteWaits=10,negative=negative)))
if __name__=='__main__':main()
