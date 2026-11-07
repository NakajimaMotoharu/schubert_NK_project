"""Independent full owning-method/source checks; reuse unchanged original parse and parse only missing files."""
from pathlib import Path
import collections,copy,datetime,hashlib,json,re,subprocess
import pg9666_pagination_static as c
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22598-remaining52-map-owners-v1';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22600-remaining52-map-owners-independent-v1';SLOT=RUNS/'pg22600-remaining52-map-owners-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
PART=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
def mask(s):return PART.sub(lambda x:''.join('\n' if c=='\n' else ' ' for c in x.group()),s)
def body_for(methods,path,cl,method,text):
 spans=methods.get((path,cl,method),[]);assert len(spans)==1,(path,cl,method);lo,hi=spans[0];return '\n'.join(text.splitlines()[lo-1:hi])
def ownership_valid(row,text,parallel,helper):
 if any(w not in text for w in row['witnesses']) or not row['reason'] or re.search(r'\bstatic\b',row['declaration']):return False
 profile=row['profile'];code=mask(text)
 if profile=='SYNCHRONOUS_LOCAL_FIXTURE':
  return not re.search(r'Executors\.\w+|new\s+Thread\b|Thread\.(?:ofPlatform|ofVirtual|startVirtualThread)|CompletableFuture|ForkJoinPool|\.parallel(?:Stream)?\s*\(|@Execution\s*\(',code) and not re.search(r'\bstatic\s+(?:final\s+)?(?:Fixture|Port)\s+\w+\s*=',code)
 if profile=='HELPER_NEW_OWNER':return 'workers.submit(() -> readOne(0))' in parallel and 'workers.submit(() -> readOne(1))' in parallel and 'var f = new Jdbc();' in helper and '.get(5, TimeUnit.SECONDS)' in parallel
 if profile=='WORKER_NEW_OWNER':
  # Constructor must occur after the submitted lambda opening, not just anywhere in the file.
  return re.search(r'\.submit\(\s*\(\) -> \{[\s\S]*?(?:Fixture\s+(?:f|fixture)\s*=\s*new Fixture\(|var\s+(?:f|fixture)\s*=\s*new Fixture\()',parallel) is not None and re.search(r'\.get\([0-9]+,\s*TimeUnit\.SECONDS\)',parallel) is not None
 if profile=='DISTINCT_PREBUILT_OWNERS':
  owners=('one','two') if Path(row['path']).stem=='LoginAttemptPortTest' else ('first','second')
  return all('Fixture '+n+' = new Fixture();' in parallel for n in owners) and all(re.search(r'(?:lock|write)\('+n+r'\s*,',parallel) for n in owners) and parallel.index('new Fixture()')<parallel.index('Executors.new') and '.get(5, TimeUnit.SECONDS)' in parallel
 if profile=='DISTINCT_OWNERS_AND_SINGLE_HANDOFF':return all(x in parallel for x in ['Fixture one = new Fixture();','Fixture two = new Fixture();','one.connection()','two.connection()','first.get(5, TimeUnit.SECONDS)','second.get(5, TimeUnit.SECONDS)']) and all(x in helper for x in ['Fixture fixture = new Fixture();','worker.submit(','fixture.connection()','task.get(5, TimeUnit.SECONDS)','fixture.assertClosed(']) and helper.index('task.get(5, TimeUnit.SECONDS)')<helper.index('fixture.assertClosed(')
 if profile=='NEW_STATEMENT_PER_CONNECTION':return all(x in text for x in ['Conn connection = new Conn(this);','new Statement(this,','final List<Conn> connections = new CopyOnWriteArrayList<>();']) and all(x in parallel for x in ['first, second','future.get(5, TimeUnit.SECONDS)','assertNotSame('])
 return False

def main():
 assert not OUT.exists() and not SLOT.exists();m=load(P/'manifest.json');assert m['actualExit']==0 and m['productTestsExecuted']==0;sites=load(P/'sites.json');assert len(sites)==52 and all(x['originalAttributes']['rule']=='UseConcurrentHashMap' for x in sites);raw=load(R/m['originalRawManifest']['path']);assert len(m['inputHashes'])==29
 for p,h in m['inputHashes'].items():assert '/src/test/java/' in p and not any(x in p for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);assert sha(R/p)==h==raw['begin']['inputHashes'][p]==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+p],cwd=R)).hexdigest()
 prior=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22410-ordinary-thread158-independent-v1/manifest.json';assert sha(prior)=='b7a9022920798dd9c82e80a3e5165fca4a19a82de4d700568c46382c86f929f4';pm=load(prior);owned=RUNS/'pg22410-ordinary-thread158-independent-v1';assert sha(R/pm['tool']['path'])==pm['tool']['sha256']==sha(owned/'source/TestMethodScopeAstCheck.java');classes={p.name:sha(p) for p in (owned/'classes').glob('*.class')};assert set(classes)=={'TestMethodScopeAstCheck.class','TestMethodScopeAstCheck$1.class'};oldparse=prior.parent/'parse.stdout';assert sha(oldparse)==pm['files']['parse.stdout'];methods={}
 def add(data):
  for line in data.splitlines():
   p,cl,method,lo,hi=line.split('\t');methods.setdefault((p,cl,method),[]).append((int(lo),int(hi)))
 add(oldparse.read_text());available={p for p,cl,method in methods};missing=sorted(set(m['inputHashes'])-available);SLOT.mkdir();stage=None;files={}
 if missing:
  c.SLOT=SLOT;stage=c.step('parse-missing',[str(R.parent/'toolchain/jdk-25.0.4/bin/java'),'-cp',str(owned/'classes'),'TestMethodScopeAstCheck',str(R),*missing],R,timeout=120);assert stage['actualExit']==0 and not stage['timedOut'];add((SLOT/'parse-missing.stdout').read_text())
 checked=[]
 for row in sites:
  p=row['path'];text=(R/p).read_text();a=row['originalAttributes'];assert text.splitlines()[row['currentDeclarationLine']-1].strip()==row['declaration'];assert 'HashMap' in row['oldAstVariable'][6] and a['variable']==row['oldAstVariable'][4];parallel='';helper=''
  if row['parallelMethod']:parallel=body_for(methods,p,Path(p).stem,row['parallelMethod'],text)
  if row['helperMethod']:
   cl=Path(p).stem+'.Fixture' if row['profile']=='NEW_STATEMENT_PER_CONNECTION' else Path(p).stem;helper=body_for(methods,p,cl,row['helperMethod'],text)
  assert ownership_valid(row,text,parallel,helper),(Path(p).name,a['variable'],row['profile']);checked.append(dict(path=p,owner=a['class'],variable=a['variable'],profile=row['profile'],parallelMethod=row['parallelMethod'],helperMethod=row['helperMethod']))
 # Reject an unknown profile, missing ownership and static-shared map metadata independently.
 sample=next(x for x in sites if x['profile']=='WORKER_NEW_OWNER');text=(R/sample['path']).read_text();parallel=body_for(methods,sample['path'],Path(sample['path']).stem,sample['parallelMethod'],text)
 for field,val in [('profile','UNKNOWN'),('witnesses',['MISSING_OWNERSHIP_WITNESS']),('declaration','static '+sample['declaration'])]:
  bad=copy.deepcopy(sample);bad[field]=val;assert not ownership_valid(bad,text,parallel,'')
 assert not ownership_valid(sample,text,'Fixture f = new Fixture(); executor.submit(() -> {});','');assert classes=={p.name:sha(p) for p in (owned/'classes').glob('*.class')};OUT.mkdir()
 if missing:
  for name in ['parse-missing.stdout','parse-missing.stderr','parse-missing-exit.safe.json']:(OUT/name).write_bytes((SLOT/name).read_bytes());files[name]=sha(OUT/name)
 result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalClassificationManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),targetSites=52,sourceFiles=29,newIndividualClassifications=52,currentRawSitesRetained=346,subsetClassifiedBefore=294,subsetClassifiedAfter=346,subsetUnclassifiedBefore=52,subsetUnclassifiedAfter=0,remainingMapSites=0,verifiedOwnershipSites=checked,profiles=dict(collections.Counter(x['profile'] for x in sites)),negativeMetadataGuards=4,sourceBytesUnchanged=True,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,effortRate=None,dynamicBehaviourRequalified=False,suppressionAdded=False,wholeF03Accepted=False,whole451Accepted=False,reusedParsedSourceFiles=29-len(missing),newlyParsedSourceFiles=len(missing),reusedParseManifest=dict(path=str(prior.relative_to(R)),sha256=sha(prior)),stage=stage,files=files,reusedToolPhysical=classes,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,classified=52,remaining=0,newParsed=len(missing))))
if __name__=='__main__':main()
