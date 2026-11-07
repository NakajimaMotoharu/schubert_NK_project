"""Five finite Future source waits in two original pure Tests; no Product execution."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';F=B/'evidence/PG22958-pure-resource-original-v1';G=B/'evidence/PG22960-pure-resource-token-guard-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());T='src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/';NAMES=['FactoryResourceScopeTest.java','ResourceScopeTest.java']
def transform(name,text):
 if name=='FactoryResourceScopeTest.java':
  assert text.count('first.get()')==text.count('second.get()')==2;return text.replace('first.get()','first.get(10, TimeUnit.SECONDS)').replace('second.get()','second.get(10, TimeUnit.SECONDS)')
 assert name=='ResourceScopeTest.java' and text.count('futures.get(i).get()')==1 and text.count('import java.util.concurrent.Future;')==1;return text.replace('import java.util.concurrent.Future;','import java.util.concurrent.Future;\nimport java.util.concurrent.TimeUnit;').replace('futures.get(i).get()','futures.get(i).get(10, TimeUnit.SECONDS)')
def main():
 phase=sys.argv[1];assert phase in ['apply','guard']
 if phase=='apply':
  assert not F.exists();base=B/'evidence/PG22954-storage-async-ownership-independent-v1/manifest.json';assert sha(base)=='c2e7721b8429fe3afe14512f9bf1d585013ecec391c2bffa7a0cd0a78f2158cd';m=load(base);assert m['actualExit']==0;c=m['currentStorage29'];assert len(c['currentInputHashes'])==29 and len(c['allCurrentRaw'])==82
  for n,h in c['currentInputHashes'].items():assert n.startswith('src/schubert-nk-storage/src/test/java/') and not any(x in n for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']) and sha(R/n)==h
  plan={n:transform(n,(R/(T+n)).read_text()) for n in NAMES};F.mkdir();tests=[]
  for name in NAMES:
   p=R/(T+name);snapshot=F/name;snapshot.write_bytes(p.read_bytes());tests.append(dict(path=T+name,className='dev.codex.schubert.nk.storage.'+name[:-5],sha256=sha(p),snapshotPath=str(snapshot.relative_to(R)),waitSites=4 if name.startswith('Factory') else 1))
  v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),tests=tests,currentStorage29=c,baseline=dict(path=str(base.relative_to(R)),sha256=sha(base)),productTestsExecuted=0);(F/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
  for item in tests:
   p=R/item['path'];assert sha(p)==item['sha256'];p.write_text(plan[p.name])
  print('original pure2 frozen; five Future waits10SECONDS');return
 assert not G.exists();m=load(F/'manifest.json');p=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';s=importlib.util.spec_from_file_location('pure_resource_token_guard',p);lib=importlib.util.module_from_spec(s);s.loader.exec_module(lib);tok=lib.java_tokens;negative=0
 for item in m['tests']:
  old=R/item['snapshotPath'];assert sha(old)==item['sha256'];expected=transform(old.name,old.read_text());actual=(R/item['path']).read_text();assert tok(expected)==tok(actual)
  for a,b in [('10, TimeUnit.SECONDS','0, TimeUnit.SECONDS'),('10, TimeUnit.SECONDS','10, TimeUnit.MINUTES')]:assert tok(actual.replace(a,b,1))!=tok(expected);negative+=1
 G.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),originalManifest=dict(path=str((F/'manifest.json').relative_to(R)),sha256=sha(F/'manifest.json')),currentHashes={i['path']:sha(R/i['path']) for i in m['tests']},finiteWaitCorrections=5,allOtherJavaTokensFixturesAndOraclesUnchanged=True,metadataNegativeGuards=negative,productTestsExecuted=0);(G/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,finiteWaits=5,negative=negative)))
if __name__=='__main__':main()
