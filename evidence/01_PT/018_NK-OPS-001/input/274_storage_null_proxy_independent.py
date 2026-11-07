"""Independent exact raw8/contract witnesses/no runtime acceptance; do not execute native/source methods."""
from pathlib import Path
import collections,copy,datetime,hashlib,importlib.util,json,subprocess,zipfile
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';P=B/'evidence/PG22842-storage-null-proxy-review-v1/manifest.json';O=B/'evidence/PG22844-storage-null-proxy-independent-v1';h=B/'input/272_storage_current_sites.py';s=importlib.util.spec_from_file_location('owned_storage_raw_post',h);lib=importlib.util.module_from_spec(s);s.loader.exec_module(lib);sha=lib.sha;load=lib.load

def valid(row,raw,inputs):
 return row['finding'] in raw and row['classification']=='NOT_APPLICABLE' and bool(row['reason'].strip()) and row['currentSourceSha256']==inputs.get(row['finding']['path']) and row['runtimeValidated'] is False and bool(row['witnesses'])
def main():
 assert not O.exists();m=load(P);baseline,raw,inputs=lib.current();assert m['actualExit']==0 and m['baseline']==baseline and m['currentInputHashes']==inputs;selected=[x for x in raw if x['rule'] in ['NullAssignment','ReturnEmptyCollectionRatherThanNull','UseProperClassLoader']];rows=m['reviewedFindings'];assert len(rows)==len(selected)==8;assert collections.Counter(json.dumps(v['finding'],sort_keys=True) for v in rows)==collections.Counter(json.dumps(v,sort_keys=True) for v in selected);assert all(valid(v,selected,inputs) for v in rows)
 for row in rows:
  f=row['finding'];text=(R/f['path']).read_text();assert sha(R/f['path'])==inputs[f['path']]
  for w in row['witnesses']:
   assert w['path']==f['path'] and sha(R/w['path'])==w['sha256'];lines=text.splitlines();assert w['text'] in '\n'.join(lines[w['line']-1:]) and text[:text.index(w['text'])].count('\n')+1==w['line']
  if f['rule']=='UseProperClassLoader':assert row['category']=='STANDALONE_FIXED_INTERFACE_PROXY_NOT_J2EE_RESOURCE_LOADER' and 'Proxy.newProxyInstance(' in text and 'new Class<?>[] {DirectoryCalls.class}' in text and 'getClass().getClassLoader()' in text
  elif f['rule']=='ReturnEmptyCollectionRatherThanNull':assert row['category']=='INVALID_PROOF_PROVIDER_NULL_ARRAY_NEGATIVE' and 'return null;' in text and 'NullPointerException.class, () -> nullIo.subject().withAdmitted(A, P, (a, p) -> 1)' in text and 'assertEquals(List.of(P, A), nullIo.closed);' in text
  elif row['category']=='INDEPENDENT_REFERENCE_ARRAY_NULL_NEGATIVE':assert 'Path[] missing = roots();' in text and 'missing[index] = null;' in text and 'assertThrows(NullPointerException.class, () -> layout(missing));' in text
  elif row['category']=='CONSUME_SINGLE_INJECTED_CLEANUP_FAULT':
   begin=text.index('Throwable failure = closeFailure;');end=text.index('raise(failure);',begin);assert 'closeFailure = null;' in text[begin:end] and 'if (closeFailure != null)' in text
  else:
   assert row['category']=='DISABLE_OPTIONAL_UNKNOWN_FAULT_IN_BOOLEAN_MATRIX';name='unknownClose' if 'LinuxStartupFileLockTest' in f['path'] else 'cleanupUnknown';assert 'f.'+name+' = '+name+' ? unknown : null;' in text and 'for (boolean '+name+' : List.of(false, true))' in text;assert name+' instanceof RuntimeException failure' in text
 rule=m['ruleSource'];assert sha(rule['path'])==rule['sha256']
 with zipfile.ZipFile(rule['path']) as z:
  data=z.read(rule['entry']);assert hashlib.sha256(data).hexdigest()==rule['entrySha256'];text=data.decode();i=text.index('name="UseProperClassLoader"');j=text.index('</description>',i);assert 'In J2EE' in text[i:j]
 assert m['primaryApi']['url'].startswith('https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Proxy.html') and not m['targetLoaderVisibilityMeasured'] and not m['proxyCreated'];neg=[]
 for k,v in [('classification','PASS'),('reason',''),('currentSourceSha256','0'*64),('runtimeValidated',True),('witnesses',[])]:
  bad=copy.deepcopy(rows[0]);bad[k]=v;assert not valid(bad,selected,inputs);neg.append(k)
 for k in ['sourceChanged','ruleConfigurationChanged','originalTestsCompiled','originalNativeTestsRun','wholeF03Accepted','whole451Accepted']:assert m[k] is False
 assert m['productTestsExecuted']==m['newAcceptance']==0 and m['rawScope']==102 and m['unclassified']==94
 O.mkdir();value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],reviewManifest=dict(path=str(P.relative_to(R)),sha256=sha(P)),baseline=baseline,checkedSources=29,reviewedRawSites=8,classificationCounts=dict(collections.Counter(v['finding']['rule'] for v in rows)),rawScope=102,individuallyClassified=8,applicableOnReviewedSubset=0,totalApplicableFindings=None,unclassified=94,metadataNegativeGuards=neg,sourceChanged=False,productTestsExecuted=0,originalTestsCompiled=False,originalNativeTestsRun=False,proxyCreated=False,targetLoaderVisibilityMeasured=False,sourceOnly=True,newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,inputHashes=inputs,primaryApi=m['primaryApi'],verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,classified=8,unclassified=94,negative=5,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
