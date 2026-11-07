"""Independent exact8 ownership metadata verification; no actual resource or Test invocation."""
from pathlib import Path
import collections,copy,datetime,hashlib,importlib.util,json
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';P=B/'evidence/PG22908-storage-resource-review-v1/manifest.json';O=B/'evidence/PG22910-storage-resource-independent-v1';s=importlib.util.spec_from_file_location('storage88_resource_post',B/'input/288_storage_current88.py');lib=importlib.util.module_from_spec(s);s.loader.exec_module(lib);sha=lib.sha

def valid(v,raw,h):return v['finding'] in raw and v['classification'] in ['NOT_APPLICABLE','APPLICABLE_SOURCE_CORRECTION_PENDING'] and v['runtimeValidated'] is False and bool(v['reason'].strip()) and bool(v['witnesses']) and v['currentSourceSha256']==h.get(v['finding']['path'])
def main():
 assert not O.exists();m=json.loads(P.read_bytes());base,raw,h,previous=lib.current();subset=[v for v in raw if v['rule'] in ['CloseResource','EmptyCatchBlock']];rows=m['reviewedFindings'];assert m['actualExit']==0 and m['baseline']==base and m['inputHashes']==h and m['previousReviewed']==previous and m['allCurrentRaw']==raw;assert len(rows)==len(subset)==8 and collections.Counter(json.dumps(v['finding'],sort_keys=True) for v in rows)==collections.Counter(json.dumps(v,sort_keys=True) for v in subset)
 categories={'DISAPPEARING_PROCFS_SNAPSHOT_ENTRY','RETURNED_WRAPPER_TRANSFERS_DELEGATE_OWNERSHIP','EXECUTOR_CANCEL_WITHOUT_TERMINATION_POSTCONDITION','NOOP_STREAM_STILL_NEEDS_LEXICAL_CLOSE','EXPLICIT_CLOSE_ORACLE_WITHOUT_FAILURE_SCOPE','ASYNC_CHILD_CLOSE_AFTER_ASSERTIONS_WITHOUT_PARENT_FALLBACK','INDEPENDENT_PARENT_CHILD_WITHOUT_EXCEPTION_SCOPES','WORKER_CHILD_CLOSE_WITHOUT_FALLBACK_SCOPE'};assert {v['category'] for v in rows}==categories
 for v in rows:
  assert valid(v,subset,h);f=v['finding'];text=(R/f['path']).read_text();assert f['method'] in text
  for w in v['witnesses']:
   p=R/w['path'];t=p.read_text();assert sha(p)==w['sha256'] and t[:t.index(w['text'])].count('\n')+1==w['line']
  if v['classification']=='NOT_APPLICABLE':assert v['category'] in ['DISAPPEARING_PROCFS_SNAPSHOT_ENTRY','RETURNED_WRAPPER_TRANSFERS_DELEGATE_OWNERSHIP'] and v['bug'] is None
  elif v['category']=='EXECUTOR_CANCEL_WITHOUT_TERMINATION_POSTCONDITION':assert v['bug']=='BUG-2461'
  else:assert v['bug']=='BUG-2460'
 assert sum(v['classification']=='NOT_APPLICABLE' for v in rows)==2;assert len(previous)==23 and all(v['classification']=='NOT_APPLICABLE' for v in previous);neg=[]
 for k,v in [('classification','PASS'),('reason',''),('currentSourceSha256','0'*64),('runtimeValidated',True),('witnesses',[])]:
  bad=copy.deepcopy(rows[0]);bad[k]=v;assert not valid(bad,subset,h);neg.append(k)
 assert m['individuallyClassified']==31 and m['unclassified']==57 and m['notApplicableOnReviewed']==25 and m['applicableOnReviewed']==6;assert not m['sourceChanged'] and not m['originalTestsCompiled'] and not m['originalNativeTestsRun'] and m['productTestsExecuted']==m['newAcceptance']==0;O.mkdir();value=dict(m,atJST=datetime.datetime.now().astimezone().isoformat(),reviewManifest=dict(path=str(P.relative_to(R)),sha256=sha(P)),metadataNegativeGuards=neg,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,reviewed=8,applicable=6,unknown=57,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
