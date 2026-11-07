"""Independent inverse token/critical-section/static binding; original native Test never invoked."""
from pathlib import Path
import collections,datetime,hashlib,importlib.util,json,re,shutil,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';PRE=RUNS/'pg22888-storage-lock-wait-prepare-v1';S=RUNS/'pg22890-storage-lock-wait-static-v1';F=B/'evidence/PG22884-storage-lock-wait-original-v1/manifest.json';G=B/'evidence/PG22886-storage-lock-wait-guard-v1/manifest.json';O=B/'evidence/PG22904-storage-lock-wait-independent-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes())
lex=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';sp=importlib.util.spec_from_file_location('lock_wait_inverse_lexer',lex);lm=importlib.util.module_from_spec(sp);sp.loader.exec_module(lm);tok=lm.java_tokens
def replace_one(ts,a,b):
 old=tok(a);new=tok(b);idx=[i for i in range(len(ts)-len(old)+1) if ts[i:i+len(old)]==old];assert len(idx)==1,(a,len(idx));i=idx[0];return ts[:i]+new+ts[i+len(old):]
def inverse(name,text):
 t=tok(text)
 if name=='PrivateChildDirectoryTest.java':
  for a,b in [('import java.util.concurrent.locks.ReentrantLock;',''),('private final ReentrantLock liveLock = new ReentrantLock();',''),('liveLock.lock(); try {','synchronized (live) {'),('} finally { liveLock.unlock(); }','}')]:t=replace_one(t,a,b)
 else:
  t=replace_one(t,'import java.util.concurrent.TimeUnit;','')
  if name=='ChildDirectoryPublicationTest.java':t=replace_one(t,'result.get(10, TimeUnit.SECONDS)','result.get()')
  else:
   assert name=='LinuxStartupAdmissionTest.java';t=replace_one(t,'executor.invokeAll(jobs, 10, TimeUnit.SECONDS)','executor.invokeAll(jobs)')
 return t

def main():
 assert not O.exists();f=load(F);g=load(G);pre=load(PRE/'manifest.json');m=load(S/'manifest.json');assert all(v['actualExit']==0 for v in [f,g,pre,m]);assert g['originalManifest']['sha256']==sha(F) and m['prepareManifestSha256']==sha(PRE/'manifest.json') and pre['currentHashes']==m['currentHashes'] and set(g['currentHashes'])==set(m['currentHashes']);negs=0
 for i in f['inputs']:
  n=i['path'];p=R/n;old=R/i['snapshotPath'];assert sha(old)==i['sha256'] and sha(p)==m['currentHashes'][n] and hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n],cwd=R)).hexdigest()==sha(p);text=p.read_text();assert inverse(p.name,text)==tok(old.read_text())
  pairs=[('liveLock.unlock();','liveLock.lock();'),('liveLock.lock();','liveLock.unlock();')] if p.name=='PrivateChildDirectoryTest.java' else [('10, TimeUnit.SECONDS','0, TimeUnit.SECONDS'),('10, TimeUnit.SECONDS','10, TimeUnit.MINUTES')]
  for a,b in pairs:
   bad=text.replace(a,b,1)
   try:ok=inverse(p.name,bad)==tok(old.read_text())
   except AssertionError:ok=False
   assert not ok;negs+=1
 for base,stages in [(PRE,pre['stages']),(S,m['stages'])]:
  for name,v in stages.items():
   assert not v['timedOut'] and v==load(base/(name+'-exit.safe.json'))
   if base==PRE:assert v['actualExit']==0
   for stream in ['stdout','stderr']:assert sha(base/(name+'.'+stream))==v[stream+'Sha256']
 for base,labels in [(PRE,['format','parse']),(S,['pmd','checkstyle'])]:
  for name in labels:
   text=(base/(name+'-class-init.stdout')).read_text();assert "Initializing 'java/lang/Object'" in text and not re.search(r"Initializing '(?:dev/codex/schubert/nk/|dev\.codex\.schubert\.nk\.)",text)
 for p,h in m['dependencies'].items():assert sha(p)==h
 own=pre['ownTool'];assert sha(R/own['path'])==own['sha256']==own['mirrorSha256']==sha(PRE/'source/TestMethodScopeAstCheck.java');assert {p.name:sha(p) for p in (PRE/'classes').iterdir()}==own['classHashes'];assert set(own['classHashes'])=={'TestMethodScopeAstCheck.class','TestMethodScopeAstCheck$1.class'};tool=(R/own['path']).read_text();assert 'task.parse()' in tool and not any(v in tool for v in ['task.analyze(','task.generate(','Class.forName']);assert pre['stages']['parse']['command'][6:]==sorted(m['currentHashes']);assert pre['stages']['own-tool-javac']['command'][-1]==str(PRE/'source/TestMethodScopeAstCheck.java')
 reports={}
 for label,tag in [('pmd','violation'),('checkstyle','error')]:
  root=E.parse(S/(label+'.xml')).getroot();items=[]
  for parent in root.iter():
   if parent.tag.rsplit('}',1)[-1]=='file':
    n=str(Path(parent.get('name')).relative_to(R));assert n in m['currentHashes'];items += [dict(path=n,**v.attrib,message=' '.join(''.join(v.itertext()).split())[:600]) for v in parent if v.tag.rsplit('}',1)[-1]==tag]
  assert items==m['reports'][label]['items'] and not m['reports'][label]['processingErrors'];reports[label]=items
 assert len(reports['pmd'])==15 and not reports['checkstyle'] and m['stages']['pmd']['actualExit']==4 and m['stages']['checkstyle']['actualExit']==0
 oldraw=f['allCurrentRaw'];assert len(oldraw)==89;paths=set(m['currentHashes']);removed=[v for v in oldraw if v['path'].endswith('/PrivateChildDirectoryTest.java') and v['rule']=='AvoidSynchronizedStatement' and v.get('class','').endswith('.Fixture')];assert len(removed)==1;oldret=[v for v in oldraw if v['path'] in paths and v not in removed];assert len(oldret)==15
 key=lambda v:tuple(v.get(k) for k in ['path','rule','class','method','variable','message']);assert collections.Counter(map(key,oldret))==collections.Counter(map(key,reports['pmd']));groups=lambda rows:{k:sorted([v for v in rows if key(v)==k],key=lambda v:(int(v['beginline']),int(v['begincolumn']))) for k in set(map(key,rows))};a=groups(oldret);z=groups(reports['pmd']);bindings=[dict(original=v,current=w) for k,vs in a.items() for v,w in zip(vs,z[k])];current=[v for v in oldraw if v['path'] not in paths]+reports['pmd'];assert len(current)==88
 hashes={n:sha(R/n) for n in f['currentInputHashes']};assert len(hashes)==29 and {n for n in hashes if hashes[n]!=f['currentInputHashes'][n]}==paths;review=[]
 for v in f['reviewedFindings']:
  if v['finding'] in removed:assert v['classification']=='APPLICABLE_SOURCE_CORRECTION_PENDING';continue
  matches=[x for x in current if (x==v['finding'] if v['finding']['path'] not in paths else key(x)==key(v['finding']))];assert len(matches)==1;row=dict(v,finding=matches[0],currentSourceSha256=hashes[v['finding']['path']]);row['witnesses']=[dict(w,sha256=sha(R/w['path']),line=(R/w['path']).read_text()[:(R/w['path']).read_text().index(w['text'])].count('\n')+1) for w in v['witnesses']];assert row['classification']=='NOT_APPLICABLE' and not row['runtimeValidated'];review.append(row)
 assert len(review)==23
 monitor_rows=[v for v in review if v['finding']['path'].endswith('/OwnedTransferDirectoryTest.java') and v['finding']['rule']=='AvoidSynchronizedStatement'];assert len(monitor_rows)==2
 for row in monitor_rows:
  missing=[v for v in current if v!=row['finding']];assert row['finding'] not in missing;negs+=1
 assert not pre['originalTestsCompiled'] and not m['originalTestsCompiled'] and m['productTestsExecuted']==pre['productTestsExecuted']==0
 failure=B/'evidence/PG22872-storage-lock-wait-original-v1/partial-failure-manifest.json';fm=load(failure);assert fm['actualExit']==1 and not fm['sourceChanged'] and fm['all29SourceHashesUnchanged'];O.mkdir();files={}
 for base,prefix in [(PRE,'prepare-'),(S,'static-')]:
  for p in base.iterdir():
   if p.is_file():name=prefix+p.name;shutil.copyfile(p,O/name);files[name]=sha(O/name)
 out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalManifest=dict(path=str(F.relative_to(R)),sha256=sha(F)),guardManifest=dict(path=str(G.relative_to(R)),sha256=sha(G)),originalPartialFailure=dict(path=str(failure.relative_to(R)),sha256=sha(failure)),sourceFixedTestFiles=3,privateMonitorCorrections=1,finiteWaitCorrections=2,independentInverseTokens=True,metadataNegativeGuards=negs,preFormatGuardHashes=g['currentHashes'],formatByteChangedSources=[n for n,h in g['currentHashes'].items() if h!=m['currentHashes'][n]],currentStorage29=dict(checkedSources=29,unchangedSources=26,changedSources=3,currentInputHashes=hashes,allCurrentRaw=current,previousComposedRaw=89,correctedSites=removed,retainedSourceRebindings=bindings,currentComposedRaw=88,reviewedFindings=review,individuallyClassified=23,unclassified=65,totalApplicableFindings=None,applicableOnReviewedSubset=0,checkstyle=0,formatDifferences=0,freshAll29EngineRun=False),bugs=['BUG-2455','BUG-2456','BUG-2457'],ykts=['YKT-2193','YKT-2194','YKT-2195'],jdkContract=dict(url='https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ExecutorService.html#invokeAll(java.util.Collection,long,java.util.concurrent.TimeUnit)',contract='All returned Futures are done; unfinished tasks cancelled on return. Future.get then reports completion/cancellation/failure. Executor.close still waits for termination; no actual cancellation/close/native-end guarantee follows from this source review.'),productTestsExecuted=0,originalTestsCompiled=False,originalNativeTestsRun=False,staticAlternativeOnly=True,ptPassCount=None,coverage=None,residualRisk='Original native/filesystem/process/Root tests remain HOLD; actual lock behavior, cancellation responsiveness, Executor.close and resource postconditions are unmeasured.',newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,files=files,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=88,classified=23,unclassified=65,negative=negs,originalTestCompileRun=0,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
