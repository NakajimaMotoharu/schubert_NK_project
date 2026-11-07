"""Independent exact16 source-owner evidence verification; no application execution."""
from pathlib import Path
import collections,copy,datetime,hashlib,importlib.util,json
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';P=B/'evidence/PG22866-storage-map-sync-review-v1/manifest.json';O=B/'evidence/PG22868-storage-map-sync-independent-v1';h=B/'input/280_storage_current89.py';s=importlib.util.spec_from_file_location('storage89_post',h);lib=importlib.util.module_from_spec(s);s.loader.exec_module(lib);sha=lib.sha

def valid(v,raw,hashes):
 return v['finding'] in raw and v['classification'] in ['NOT_APPLICABLE','APPLICABLE_SOURCE_CORRECTION_PENDING'] and v['currentSourceSha256']==hashes.get(v['finding']['path']) and v['runtimeValidated'] is False and bool(v['reason'].strip()) and bool(v['witnesses'])
def main():
 assert not O.exists();m=json.loads(P.read_bytes());base,raw,hashes,previous=lib.current();rows=m['reviewedFindings'];subset=[v for v in raw if v['rule'] in ['UseConcurrentHashMap','AvoidSynchronizedStatement']];assert len(rows)==len(subset)==16;assert collections.Counter(json.dumps(v['finding'],sort_keys=True) for v in rows)==collections.Counter(json.dumps(v,sort_keys=True) for v in subset);assert m['inputHashes']==hashes and m['baseline']==base and m['previousReviewed']==previous
 for v in rows:
  assert valid(v,subset,hashes);f=v['finding'];text=(R/f['path']).read_text();assert f['rule']=='UseConcurrentHashMap' and 'new HashMap' in text or f['rule']=='AvoidSynchronizedStatement' and 'synchronized (' in text
  for w in v['witnesses']:
   p=R/w['path'];source=p.read_text();assert sha(p)==w['sha256'] and source[:source.index(w['text'])].count('\n')+1==w['line']
  if v['classification']=='APPLICABLE_SOURCE_CORRECTION_PENDING':assert f['path'].endswith('/PrivateChildDirectoryTest.java') and f['class'].endswith('.Fixture') and v['category']=='PRIVATE_FD_BOOKKEEPING_MONITOR_STYLE'
  elif f['rule']=='AvoidSynchronizedStatement':assert v['category']=='PUBLIC_MONITOR_INDEPENDENCE_REGRESSION_ORACLE' and not f.get('class','').endswith('.Fixture')
  if v['category']=='FRESH_SYNCHRONOUS_NULL_NEGATIVE_ATTRIBUTE_MAP':assert 'missing.put(name, null)' in text and not any(x in text for x in ['Executors.','new Thread(','Thread.of','submit('])
  if v['category']=='FRESH_METHOD_LOCAL_SEQUENTIAL_ATTRIBUTE_MATRIX':assert f['method']=='a07MetadataAndProviderNegativeMatrix' and not any(x in text for x in ['Executors.','new Thread(','Thread.of','submit('])
 assert collections.Counter(v['finding']['rule'] for v in rows)=={'UseConcurrentHashMap':11,'AvoidSynchronizedStatement':5};assert sum(v['classification']=='NOT_APPLICABLE' for v in rows)==15;assert len(previous)==8 and all(v['classification']=='NOT_APPLICABLE' for v in previous);assert m['individuallyClassified']==24 and m['notApplicableOnReviewed']==23 and m['applicableOnReviewed']==1 and m['unclassified']==65
 negatives=[]
 for k,v in [('classification','PASS'),('reason',''),('currentSourceSha256','0'*64),('runtimeValidated',True),('witnesses',[])]:
  b=copy.deepcopy(rows[0]);b[k]=v;assert not valid(b,subset,hashes);negatives.append(k)
 for k in ['sourceChanged','ruleConfigurationChanged','originalTestsCompiled','originalNativeTestsRun','wholeF03Accepted','whole451Accepted']:assert m[k] is False
 assert m['productTestsExecuted']==m['newAcceptance']==0;O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],reviewManifest=dict(path=str(P.relative_to(R)),sha256=sha(P)),baseline=base,inputHashes=hashes,reviewedFindings=rows,previousReviewed=previous,rawScope=89,individuallyClassified=24,notApplicableOnReviewed=23,applicableOnReviewed=1,totalApplicableFindings=None,unclassified=65,metadataNegativeGuards=negatives,productTestsExecuted=0,originalTestsCompiled=False,originalNativeTestsRun=False,newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,classified=24,applicable=1,unknown=65,negative=5,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
