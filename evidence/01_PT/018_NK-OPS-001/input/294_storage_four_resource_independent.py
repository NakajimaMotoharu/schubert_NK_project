"""Independent lexical scope inverse and current diagnostics binding; no resource/Test execution."""
from pathlib import Path
import collections,datetime,hashlib,importlib.util,json,re,shutil,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';PRE=RUNS/'pg22918-storage-four-resource-prepare-v1';S=RUNS/'pg22920-storage-four-resource-static-v1';F=B/'evidence/PG22914-storage-four-resource-original-v1/manifest.json';G=B/'evidence/PG22916-storage-four-resource-guard-v1/manifest.json';O=B/'evidence/PG22934-storage-four-resource-independent-v2';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());sp=importlib.util.spec_from_file_location('resource_scope_inverse_lexer',R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py');lm=importlib.util.module_from_spec(sp);sp.loader.exec_module(lm);tok=lm.java_tokens

def locate(t,part):
 p=tok(part);a=[i for i in range(len(t)-len(p)+1) if t[i:i+len(p)]==p];assert len(a)==1,(part,len(a));return a[0],len(p)
def unwrap(t,marker):
 i,_=locate(t,marker);assert t[i:i+2]==['try','('];depth=0;j=i+1
 while j<len(t):
  if t[j]=='(':depth+=1
  if t[j]==')':
   depth-=1
   if depth==0:break
  j+=1
 assert t[j+1]=='{';depth=1;k=j+2
 while depth:
  if t[k]=='{':depth+=1
  if t[k]=='}':depth-=1
  k+=1
 return t[:i]+t[i+2:j]+[';']+t[j+2:k-1]+t[k:]
def method_span(t,name):
 i,_=locate(t,'void '+name+'(');j=i
 while t[j]!='{':j+=1
 depth=1;k=j+1
 while depth:
  if t[k]=='{':depth+=1
  if t[k]=='}':depth-=1
  k+=1
 return i,k
def inverse(name,text):
 t=tok(text)
 if name=='OwnedDirectoryFactoryTest.java':return unwrap(t,'try (var root = OwnedTransferDirectory.openRoot(calls))')
 if name=='StorageRootInspectionTest.java':return unwrap(t,'try (DirectoryStream<Path> ordinary =')
 assert name=='OwnedTransferDirectoryTest.java';i,k=method_span(t,'f02ExistingDateIndependentChildLifetimeAndSafeIoFailures');t=t[:i]+unwrap(t[i:k],'try (var parent = OwnedTransferDirectory.open(calls, root); var child = parent.openDate(DATE))')+t[k:];a='try (var parent = OwnedTransferDirectory.open(calls, root); var child = parent.openDate(DATE); var executor = Executors.newFixedThreadPool(2)) {';b='try (var parent = OwnedTransferDirectory.open(calls, root); var executor = Executors.newFixedThreadPool(2)) { var child = parent.openDate(DATE);';i,n=locate(t,a);return t[:i]+tok(b)+t[i+n:]
def main():
 assert not O.exists();f=load(F);g=load(G);pre=load(PRE/'manifest.json');m=load(S/'manifest.json');assert all(v['actualExit']==0 for v in [f,g,pre,m]);assert g['originalManifest']['sha256']==sha(F) and m['prepareManifestSha256']==sha(PRE/'manifest.json') and pre['currentHashes']==m['currentHashes'] and set(g['currentHashes'])==set(m['currentHashes']);negative=0
 for item in f['inputs']:
  n=item['path'];p=R/n;old=R/item['snapshotPath'];assert sha(old)==item['sha256'] and sha(p)==m['currentHashes'][n] and hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n],cwd=R)).hexdigest()==sha(p);text=p.read_text();assert inverse(p.name,text)==tok(old.read_text())
  markers=['try (var root ='] if p.name=='OwnedDirectoryFactoryTest.java' else ['try (DirectoryStream<Path> ordinary ='] if p.name=='StorageRootInspectionTest.java' else ['try (var parent = OwnedTransferDirectory.open(calls, root);\n        var child = parent.openDate(DATE))','var child = parent.openDate(DATE);\n        var executor = Executors.newFixedThreadPool(2)']
  for marker in markers:
   assert marker in text;bad=text.replace(marker,'MISSING_OWNERSHIP',1)
   try:ok=inverse(p.name,bad)==tok(old.read_text())
   except AssertionError:ok=False
   assert not ok;negative+=1
 owned=next(v for v in f['inputs'] if v['path'].endswith('/OwnedTransferDirectoryTest.java'));owned_tokens=tok((R/owned['path']).read_text())
 for name in ['f02ExistingDateIndependentChildLifetimeAndSafeIoFailures','f02CloseCannotReuseDescriptorWhileFileCallbackIsInFlight']:
  span=method_span(owned_tokens,name);assert owned_tokens[span[0]:span[0]+2]==['void',name];bad=[name+'_WRONG_OWNER' if v==name else v for v in owned_tokens]
  try:method_span(bad,name);rejected=False
  except AssertionError:rejected=True
  assert rejected;negative+=1
 for base,stages in [(PRE,pre['stages']),(S,m['stages'])]:
  for label,v in stages.items():
   assert not v['timedOut'] and v==load(base/(label+'-exit.safe.json'))
   if base==PRE:assert v['actualExit']==0
   for stream in ['stdout','stderr']:assert sha(base/(label+'.'+stream))==v[stream+'Sha256']
 for base,labels in [(PRE,['format','parse']),(S,['pmd','checkstyle'])]:
  for label in labels:
   text=(base/(label+'-class-init.stdout')).read_text();assert "Initializing 'java/lang/Object'" in text and not re.search(r"Initializing '(?:dev/codex/schubert/nk/|dev\.codex\.schubert\.nk\.)",text)
 for p,h in m['dependencies'].items():assert sha(p)==h
 own=pre['ownTool'];assert sha(R/own['path'])==own['sha256']==own['mirrorSha256']==sha(PRE/'source/TestMethodScopeAstCheck.java');assert {p.name:sha(p) for p in (PRE/'classes').iterdir()}==own['classHashes'] and set(own['classHashes'])=={'TestMethodScopeAstCheck.class','TestMethodScopeAstCheck$1.class'};text=(R/own['path']).read_text();assert 'task.parse()' in text and not any(x in text for x in ['task.analyze(','task.generate(','Class.forName']);assert pre['stages']['parse']['command'][6:]==sorted(m['currentHashes']);assert pre['stages']['own-tool-javac']['command'][-1]==str(PRE/'source/TestMethodScopeAstCheck.java')
 reports={}
 for label,tag in [('pmd','violation'),('checkstyle','error')]:
  root=E.parse(S/(label+'.xml')).getroot();items=[]
  for parent in root.iter():
   if parent.tag.rsplit('}',1)[-1]=='file':
    n=str(Path(parent.get('name')).relative_to(R));assert n in m['currentHashes'];items += [dict(path=n,**v.attrib,message=' '.join(''.join(v.itertext()).split())[:600]) for v in parent if v.tag.rsplit('}',1)[-1]==tag]
  assert items==m['reports'][label]['items'] and not m['reports'][label]['processingErrors'];reports[label]=items
 assert len(reports['pmd'])==20 and not reports['checkstyle'] and m['stages']['pmd']['actualExit']==4 and m['stages']['checkstyle']['actualExit']==0
 old=f['allCurrentRaw'];paths=set(m['currentHashes']);removed=[v for v in old if v['rule']=='CloseResource' and (v['path'].endswith('/OwnedDirectoryFactoryTest.java') or v['path'].endswith('/StorageRootInspectionTest.java') or v.get('method') in ['f02ExistingDateIndependentChildLifetimeAndSafeIoFailures','f02CloseCannotReuseDescriptorWhileFileCallbackIsInFlight'])];assert len(removed)==4;retained=[v for v in old if v['path'] in paths and v not in removed];key=lambda v:tuple(v.get(k) for k in ['path','rule','class','method','variable','message']);assert len(retained)==24-4 and collections.Counter(map(key,retained))==collections.Counter(map(key,reports['pmd']));groups=lambda rows:{k:sorted([v for v in rows if key(v)==k],key=lambda v:(int(v['beginline']),int(v['begincolumn']))) for k in set(map(key,rows))};a=groups(retained);z=groups(reports['pmd']);bindings=[dict(original=v,current=w) for k,vs in a.items() for v,w in zip(vs,z[k])];fullkey=lambda v:tuple(v.get(k) for k in ['path','rule','beginline','begincolumn','endline','endcolumn']);mapping={fullkey(v['original']):v['current'] for v in bindings};current=[v for v in old if v['path'] not in paths]+reports['pmd'];assert len(current)==84;hashes={n:sha(R/n) for n in f['currentInputHashes']};assert len(hashes)==29 and {n for n in hashes if hashes[n]!=f['currentInputHashes'][n]}==paths;reviews=[]
 for oldrow in f['reviewedFindings']:
  v=oldrow['finding']
  if v in removed:assert oldrow['classification']=='APPLICABLE_SOURCE_CORRECTION_PENDING';continue
  new=mapping[fullkey(v)] if v['path'] in paths else v;assert new in current;row=dict(oldrow,finding=new,currentSourceSha256=hashes[v['path']]);row['witnesses']=[dict(w,sha256=sha(R/w['path']),line=(R/w['path']).read_text()[:(R/w['path']).read_text().index(w['text'])].count('\n')+1) for w in oldrow['witnesses']];assert not row['runtimeValidated'];reviews.append(row)
 assert len(reviews)==27 and sum(v['classification']=='NOT_APPLICABLE' for v in reviews)==25 and sum(v['classification']=='APPLICABLE_SOURCE_CORRECTION_PENDING' for v in reviews)==2;assert not m['originalTestsCompiled'] and not pre['originalTestsCompiled'] and m['productTestsExecuted']==pre['productTestsExecuted']==0;O.mkdir();files={}
 for base,prefix in [(PRE,'prepare-'),(S,'static-')]:
  for p in base.iterdir():
   if p.is_file():name=prefix+p.name;shutil.copyfile(p,O/name);files[name]=sha(O/name)
 out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalManifest=dict(path=str(F.relative_to(R)),sha256=sha(F)),guardManifest=dict(path=str(G.relative_to(R)),sha256=sha(G)),sourceFixedTestFiles=3,correctedOwnershipSites=4,independentInverseAllOriginalTokens=True,metadataNegativeGuards=negative,preFormatGuardHashes=g['currentHashes'],formatByteChangedSources=[n for n,h in g['currentHashes'].items() if h!=m['currentHashes'][n]],currentStorage29=dict(checkedSources=29,unchangedSources=26,changedSources=3,currentInputHashes=hashes,allCurrentRaw=current,previousComposedRaw=88,correctedSites=removed,retainedSourceRebindings=bindings,currentComposedRaw=84,reviewedFindings=reviews,individuallyClassified=27,notApplicableOnReviewed=25,applicableOnReviewedSubset=2,unclassified=57,totalApplicableFindings=None,checkstyle=0,formatDifferences=0,freshAll29EngineRun=False),bug='BUG-2460',ykt='YKT-2198',productTestsExecuted=0,originalTestsCompiled=False,originalNativeTestsRun=False,staticAlternativeOnly=True,ptPassCount=None,coverage=None,residualRisk='Four lexical ownership guards statically corrected only; actual native teardown/worker completion unmeasured. BUG036 async child fallback and BUG2461 executor termination remain source-pending. All original native/Root/filesystem/process runtime holds retained.',newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,files=files,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,corrected=4,raw=84,classified=27,pending=2,unknown=57,negative=negative,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
