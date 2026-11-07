"""Independent ten wait token inverses and82 current source reason bindings; no original Test/native run."""
from pathlib import Path
import collections,datetime,hashlib,importlib.util,json,re,shutil,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';PRE=RUNS/'pg23010-storage-ten-wait-prepare-v1';S=RUNS/'pg23012-storage-ten-wait-static-v1';F=B/'evidence/PG23006-storage-ten-wait-original-v1/manifest.json';G=B/'evidence/PG23008-storage-ten-wait-guard-v1/manifest.json';O=B/'evidence/PG23014-storage-ten-wait-independent-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());sp=importlib.util.spec_from_file_location('ten_wait_inverse_lexer',R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py');lib=importlib.util.module_from_spec(sp);sp.loader.exec_module(lib);tok=lib.java_tokens
VALUES={'LinuxExecDescriptorsTest.java':('executor.invokeAll(work, 30, TimeUnit.SECONDS)','executor.invokeAll(work)',1),'LinuxHostDirectoryCallsTest.java':('executor.invokeAll(work, 30, TimeUnit.SECONDS)','executor.invokeAll(work)',1),'LinuxInodeSecurityTest.java':('pool.invokeAll(tasks, 30, TimeUnit.SECONDS)','pool.invokeAll(tasks)',1),'LinuxProcessExecTest.java':('executor.invokeAll(work, 30, TimeUnit.SECONDS)','executor.invokeAll(work)',1),'LinuxDirectoryCallsTest.java':('executor.invokeAll(tasks, 30, TimeUnit.SECONDS)','executor.invokeAll(tasks)',2),'LinuxSealedProofTest.java':('executor.invokeAll(work, 30, TimeUnit.SECONDS)','executor.invokeAll(work)',1),'LinuxFileLockTest.java':('executor.invokeAll(work, 30, TimeUnit.SECONDS)','executor.invokeAll(work)',1),'LinuxStartupFileLockTest.java':('executor.invokeAll(work, 30, TimeUnit.SECONDS)','executor.invokeAll(work)',1),'ServiceConfigFilesTest.java':('job.get(10, TimeUnit.SECONDS)','job.get()',1)}
def replaced(ts,a,b,count):
 old=tok(a);new=tok(b);indices=[i for i in range(len(ts)-len(old)+1) if ts[i:i+len(old)]==old];assert len(indices)==count
 for i in reversed(indices):ts=ts[:i]+new+ts[i+len(old):]
 return ts
def inverse(name,text,added):
 a,b,count=VALUES[name];t=replaced(tok(text),a,b,count)
 if added:t=replaced(t,'import java.util.concurrent.TimeUnit;','',1)
 return t

def main():
 assert not O.exists();f=load(F);g=load(G);pre=load(PRE/'manifest.json');m=load(S/'manifest.json');assert all(v['actualExit']==0 for v in [f,g,pre,m]);assert g['originalManifest']['sha256']==sha(F) and m['prepareManifestSha256']==sha(PRE/'manifest.json') and pre['currentHashes']==m['currentHashes'] and set(g['currentHashes'])==set(m['currentHashes']);negative=0;waits=0;snapshots={}
 for item in f['inputs']:
  n=item['path'];p=R/n;old=R/item['snapshotPath'];snapshots[n]=old;assert sha(old)==item['sha256'] and sha(p)==m['currentHashes'][n] and hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n],cwd=R)).hexdigest()==sha(p);actual=p.read_text();assert inverse(p.name,actual,item['addedTimeUnitImport'])==tok(old.read_text());waits+=VALUES[p.name][2]
  deadline='10, TimeUnit.SECONDS' if p.name=='ServiceConfigFilesTest.java' else '30, TimeUnit.SECONDS'
  for bad in [actual.replace(deadline,'0, TimeUnit.SECONDS',1),actual.replace(deadline,deadline.replace('SECONDS','MINUTES'),1),actual.replace('assertEquals(', 'assertNotEquals(',1)]:
   assert bad!=actual
   try:ok=inverse(p.name,bad,item['addedTimeUnitImport'])==tok(old.read_text())
   except AssertionError:ok=False
   assert not ok;negative+=1
 assert waits==10 and len(snapshots)==9 and sum(v['addedTimeUnitImport'] for v in f['inputs'])==2
 for base,stages in [(PRE,pre['stages']),(S,m['stages'])]:
  for label,v in stages.items():
   assert not v['timedOut'] and v==load(base/(label+'-exit.safe.json'))
   if base==PRE:assert v['actualExit']==0
   for stream in ['stdout','stderr']:assert sha(base/(label+'.'+stream))==v[stream+'Sha256']
 for base,labels in [(PRE,['format','parse']),(S,['pmd','checkstyle'])]:
  for label in labels:
   text=(base/(label+'-class-init.stdout')).read_text();assert "Initializing 'java/lang/Object'" in text and not re.search(r"Initializing '(?:dev/codex/schubert/nk/|dev\.codex\.schubert\.nk\.)",text)
 for p,h in m['dependencies'].items():assert sha(p)==h
 own=pre['ownTool'];assert sha(R/own['path'])==own['sha256']==own['mirrorSha256']==sha(PRE/'source/TestMethodScopeAstCheck.java');assert {p.name:sha(p) for p in (PRE/'classes').iterdir()}==own['classHashes'] and set(own['classHashes'])=={'TestMethodScopeAstCheck.class','TestMethodScopeAstCheck$1.class'};text=(R/own['path']).read_text();assert 'task.parse()' in text and not any(x in text for x in ['task.analyze(','task.generate(','Class.forName']);assert pre['stages']['parse']['command'][6:]==sorted(m['currentHashes']) and pre['stages']['own-tool-javac']['command'][-1]==str(PRE/'source/TestMethodScopeAstCheck.java');methods=[]
 for line in (PRE/'parse.stdout').read_text().splitlines():
  path,owner,method,begin,end=line.split('\t');assert path in m['currentHashes'];methods.append(dict(path=path,owner=owner,method=method,beginline=int(begin),endline=int(end)))
 reports={}
 for label,tag in [('pmd','violation'),('checkstyle','error')]:
  root=E.parse(S/(label+'.xml')).getroot();items=[]
  for parent in root.iter():
   if parent.tag.rsplit('}',1)[-1]=='file':
    n=str(Path(parent.get('name')).relative_to(R));assert n in m['currentHashes'];items += [dict(path=n,**v.attrib,message=' '.join(''.join(v.itertext()).split())[:600]) for v in parent if v.tag.rsplit('}',1)[-1]==tag]
  assert items==m['reports'][label]['items'] and not m['reports'][label]['processingErrors'];reports[label]=items
 assert len(reports['pmd'])==26 and not reports['checkstyle'] and m['stages']['pmd']['actualExit']==4 and m['stages']['checkstyle']['actualExit']==0;oldscope=f['currentStorage29'];old=oldscope['allCurrentRaw'];paths=set(m['currentHashes']);oldsites=[v for v in old if v['path'] in paths];key=lambda v:tuple(v.get(k) for k in ['path','rule','class','method','variable','message']);assert len(oldsites)==26 and collections.Counter(map(key,oldsites))==collections.Counter(map(key,reports['pmd']));groups=lambda rows:{k:sorted([v for v in rows if key(v)==k],key=lambda v:(int(v['beginline']),int(v['begincolumn']))) for k in set(map(key,rows))};a=groups(oldsites);z=groups(reports['pmd']);bindings=[dict(original=v,current=w) for k,vs in a.items() for v,w in zip(vs,z[k])];fullkey=lambda v:tuple(v.get(k) for k in ['path','rule','beginline','begincolumn','endline','endcolumn']);mapping={fullkey(v['original']):v['current'] for v in bindings};current=[v for v in old if v['path'] not in paths]+reports['pmd'];assert len(current)==82;hashes={n:sha(R/n) for n in oldscope['currentInputHashes']};assert len(hashes)==29 and {n for n,h in hashes.items() if h!=oldscope['currentInputHashes'][n]}==paths;reviews=[];boundMethods={};changedThreadSites=0;newFiniteReasonSites=0
 for oldrow in oldscope['reviewedFindings']:
  f0=oldrow['finding'];n=f0['path'];v=mapping[fullkey(f0)] if n in paths else f0;assert v in current;row=dict(oldrow,finding=v,currentSourceSha256=hashes[n]);assert row['classification']=='NOT_APPLICABLE'
  if n in paths and v['rule']=='DoNotUseThreads':
   changedThreadSites+=1;matches=[s for s in methods if s['path']==n and s['owner']==v['class'] and s['method']==v['method'] and s['beginline']<=int(v['beginline'])<=int(v['endline'])<=s['endline']];assert len(matches)==1;scope=matches[0];lines=(R/n).read_text().splitlines();body='\n'.join(lines[scope['beginline']-1:scope['endline']]);before=oldrow['methodScope'];oldlines=snapshots[n].read_text().splitlines();oldbody='\n'.join(oldlines[before['beginline']-1:before['endline']]);assert hashlib.sha256(oldbody.encode()).hexdigest()==oldrow['methodBodySha256'];row.update(methodScope=scope,methodBodySha256=hashlib.sha256(body.encode()).hexdigest());boundMethods[row['methodKey']]=dict(scope,bodySha256=row['methodBodySha256'])
   if tok(body)!=tok(oldbody):
    newFiniteReasonSites+=1;row['previousReason']=oldrow['reason'];row['reason']='Current original standalone JUnit method remains outside the installed J2EE application-thread context. BUG2466 source correction adds bulk30SECONDS or submitted Future10SECONDS with all other tokens/fixtures/oracles unchanged; prior reason is historical in previousReason. TWR ownership remains, actual native/process/FFM/filesystem completion and cancellation/close bounds are unmeasured HOLD. BUG2467 process owner issues stay separate.';row['deadlineSourceCorrected']=True
  if n in paths and 'witnesses' in row:
   updated=[]
   for w in row['witnesses']:
    source=(R/w['path']).read_text();assert w['text'] in source;updated.append(dict(w,sha256=sha(R/w['path']),line=source[:source.index(w['text'])].count('\n')+1))
   row['witnesses']=updated
  reviews.append(row)
 assert len(reviews)==82 and changedThreadSites==24 and newFiniteReasonSites==20;assert len({fullkey(v['finding']) for v in reviews})==82 and collections.Counter(fullkey(v['finding']) for v in reviews)==collections.Counter(map(fullkey,current));assert not m['originalTestsCompiled'] and not pre['originalTestsCompiled'] and m['productTestsExecuted']==pre['productTestsExecuted']==0;O.mkdir();files={}
 for base,prefix in [(PRE,'prepare-'),(S,'static-')]:
  for p in base.iterdir():
   if p.is_file():name=prefix+p.name;shutil.copyfile(p,O/name);files[name]=sha(O/name)
 out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalManifest=dict(path=str(F.relative_to(R)),sha256=sha(F)),guardManifest=dict(path=str(G.relative_to(R)),sha256=sha(G)),sourceFixedTestFiles=9,finiteWaitCorrections=10,bulkDeadlines30Seconds=9,submittedFutureDeadlines10Seconds=1,allOtherJavaTokensFixturesAndOraclesRestored=True,metadataNegativeGuards=negative,preFormatGuardHashes=g['currentHashes'],formatByteChangedSources=[n for n,h in g['currentHashes'].items() if h!=m['currentHashes'][n]],currentStorage29=dict(checkedSources=29,unchangedSources=20,changedSources=9,currentInputHashes=hashes,allCurrentRaw=current,retainedSourceRebindings=bindings,currentComposedRaw=82,reviewedFindings=reviews,individuallyClassified=82,applicableOnReviewedSubset=0,totalApplicableFindings=0,unclassified=0,reboundRawSites=26,reboundThreadSites=24,reboundUnchangedNullSentinels=2,newFiniteReasonSites=20,updatedMethodScopes=boundMethods,checkstyle=0,formatDifferences=0,freshAll29EngineRun=False),bug='BUG-2466',ykt='YKT-2204',originalTestsCompiled=False,productTestsExecuted=0,originalNativeTestsRun=False,staticAlternativeOnly=True,ptPassCount=None,coverage=None,residualRisk='Native/process/FFM/filesystem/Root Test runtime remains HOLD. Cancellation responsiveness/Executor.close/native terminal bounds unmeasured. BUG2467/YKT2205 eight process-owner candidates require source review/remedy; no process action performed.',openProcessDefect='BUG-2467',wholeStorageQualityAccepted=False,newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,files=files,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,finiteWaits=10,raw=82,classified=82,unknown=0,reboundRaw=26,reboundThread=24,negative=negative,originalTestCompileRun=0,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
