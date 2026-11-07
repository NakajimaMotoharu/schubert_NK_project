"""Finite old qualification metadata supplement, no Test/production/compiler execution."""
from pathlib import Path
import json,hashlib,datetime,zipfile,collections,re
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'PMO/pgpt-completion-stage-20261102';O=B/'evidence/PG23360-base59-named-proof-supplement-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def crc64(data):
 v=0
 for b in data:
  v^=b
  for _ in range(8):v=(v>>1)^0xd800000000000000 if v&1 else v>>1
 return f'{v:016x}'

def metadata(data):
 assert data[:4]==bytes.fromhex('cafebabe');pool={};p=10;i=1;count=int.from_bytes(data[8:10],'big')
 while i<count:
  t=data[p];p+=1
  if t==1:n=int.from_bytes(data[p:p+2],'big');p+=2;pool[i]=data[p:p+n].decode('utf8','replace');p+=n
  elif t in (7,8,16,19,20):pool[i]=int.from_bytes(data[p:p+2],'big');p+=2
  elif t in (3,4,9,10,11,12,17,18):p+=4
  elif t in (5,6):p+=8;i+=1
  elif t==15:p+=3
  else:raise AssertionError(t)
  i+=1
 name=pool[pool[int.from_bytes(data[p+2:p+4],'big')]];p+=6;n=int.from_bytes(data[p:p+2],'big');p+=2+2*n
 def attrs(p):
  n=int.from_bytes(data[p:p+2],'big');p+=2;out={}
  for _ in range(n):
   k=pool[int.from_bytes(data[p:p+2],'big')];length=int.from_bytes(data[p+2:p+6],'big');p+=6;out[k]=data[p:p+length];p+=length
  return p,out
 methods=[]
 for section in range(2):
  n=int.from_bytes(data[p:p+2],'big');p+=2
  for _ in range(n):
   label=pool[int.from_bytes(data[p+2:p+4],'big')];descriptor=pool[int.from_bytes(data[p+4:p+6],'big')];p+=6;p,a=attrs(p)
   if section:methods.append(dict(name=label,descriptor=descriptor,code='Code' in a))
 p,a=attrs(p);assert p==len(data);return dict(name=name,sourceFile=pool[int.from_bytes(a['SourceFile'],'big')],methods=methods)
assert not O.exists();ledger=S/'cost-ledger.json';cost=load(ledger);quals={k:v for k,v in cost.items() if 'qualification' in k.lower() and not k.startswith('latest') and isinstance(v,dict)};assert len(quals)==19
normal=R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5';classes={};sourcePhysical=collections.defaultdict(list)
for module,j in nm['jars'].items():
 jar=Path(j['path']);assert sha(jar)==j['sha256']
 with zipfile.ZipFile(jar) as z:
  for n in z.namelist():
   if n.endswith('.class'):
    data=z.read(n);meta=metadata(data);fqn=n[:-6];source='src/schubert-nk-'+module+'/src/main/java/'+fqn.rsplit('/',1)[0]+'/'+meta['sourceFile'];assert source in nm['begin']['inputHashes'];assert fqn not in classes;classes[fqn]=dict(path=source,sha256=hashlib.sha256(data).hexdigest(),crc64=crc64(data),hasCode=any(x['code'] for x in meta['methods']));sourcePhysical[source].append(fqn)
blocked=('RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest','SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness');reads={};declines=[];cache={}
def readref(n):
 p=Path(n);p=R/p if not p.is_absolute() else p
 if not p.is_relative_to(R) or p.suffix!='.json' or not str(p.relative_to(R)).startswith('evidence/01_PT/') or any(w in str(p) for w in blocked):return None
 assert p.is_file() and not p.is_symlink()
 if p.stat().st_size>2*1024*1024:declines.append(dict(path=str(p.relative_to(R)),reason='PUBLIC_METADATA_ABOVE_DECLARED_2M_BOUND_NOT_READ'));return None
 key=str(p.relative_to(R))
 if key not in cache:cache[key]=load(p);reads[key]=sha(p)
 return key,cache[key]
def strings(v):
 if isinstance(v,str):yield v
 elif isinstance(v,dict):
  for k,x in v.items():
   yield k;yield from strings(x)
 elif isinstance(v,list):
  for x in v:yield from strings(x)
rows={};summaries=[]
def add(n,origin,ref):
 if n not in classes:return
 p=classes[n]['path'];entry=rows.setdefault(p,dict(path=p,currentSourceSha256=nm['begin']['inputHashes'][p],normalPhysical={f:classes[f] for f in sourcePhysical[p]},origins=[],publicManifestRefs=[],wholeQualificationTransferred=False));
 if origin not in entry['origins']:entry['origins'].append(origin)
 if ref and ref not in entry['publicManifestRefs']:entry['publicManifestRefs'].append(ref)
for key,value in quals.items():
 refs=[]
 for n in sorted(set(strings(value))):
  if n.endswith('.json'):
   ref=readref(n)
   if ref:refs.append(ref)
 for n in strings(value):
  if n.startswith('dev/codex/schubert/nk/') and n in classes:add(n,dict(field=key,kind='EXPLICIT_CLASS_NAME_IN_OLD_QUALIFICATION_NOT_WHOLE_PROOF'),None)
 for p,v in refs:
  # Only explicit target coverage/physical/source-unit fields; never universal inputHashes.
  for field in ['coverage','fullSourceUnits','physicalHashes','physicalClasses','physical','sourcePhysicalInventory','targetPhysical','mainPaths','targetSources','targetSource','mainSource','mainPath']:
   if field not in v:continue
   for n in strings(v[field]):
    if n in classes:add(n,dict(field=key,manifestField=field,kind='EXPLICIT_QUALIFICATION_TARGET_CANDIDATE'),dict(path=p,sha256=reads[p]))
    elif n in sourcePhysical:
     for f in sourcePhysical[n]:add(f,dict(field=key,manifestField=field,kind='EXPLICIT_QUALIFICATION_SOURCE_CANDIDATE'),dict(path=p,sha256=reads[p]))
 summaries.append(dict(field=key,originalSource=value.get('source'),originalRun=value.get('run'),originalTests=value.get('tests'),refs=[dict(path=p,sha256=reads[p],actualExit=v.get('actualExit')) for p,v in refs]))
# Explicit known five-test command metadata subproof: compare existing published proof with current
# normal class bytes and source pins without reading old exec/XML/class or re-running old tests.
q=cost['commandMetadataQualification'];qp=R/q['manifest'];qm=load(qp);assert sha(qp)==q['manifestSha256'];n='dev/codex/schubert/nk/api/application/question/QuestionCommandMetadata';source=classes[n]['path'];assert qm['actualExit']==0 and qm['tests']==5 and qm['wholeSourceFourCounter100'];assert qm['physicalHashes'][n]==classes[n]['sha256'];assert qm['physicalClassIds'][n]==classes[n]['crc64'];assert qm['inputHashes'][source]==nm['begin']['inputHashes'][source]==sha(R/source);assert all(x['missed']==0 for x in qm['coverage'][n].values());assert qm['coverage'][n]['LINE']['covered']==9 and qm['coverage'][n]['METHOD']['covered']==2 and qm['coverage'][n]['BRANCH']['covered']==4
question=dict(path=source,sourceSha256=sha(R/source),physical={n:classes[n]},proof=dict(path=str(qp.relative_to(R)),sha256=sha(qp)),oldSource=qm['source'],currentNormalSource=nm['source'],tests=5,sameSourceAndNormalPhysical=True,coverage=qm['coverage'][n],previouslyCountedInPartial80=True,registeredComponentDelta=0,newSourceProofs=0,reexecutionRequiredForConfirmation=False,formalAcceptanceTransferred=False)
priorp=B/'evidence/PG23274-named-roster-duplicate-post-v1/candidate-source-rows.json';prior=load(priorp);priorNames={v['path'] for v in prior};union=sorted(priorNames|set(rows));added=sorted(set(rows)-priorNames);O.mkdir();files={}
for name,v in [('selected-qualification-summaries.json',summaries),('supplemental-source-candidates.json',list(rows.values())),('current-normal-physical-index.json',classes),('existing-question-five-proof.json',question),('candidate-name-union.json',union)]:
 p=O/name;p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');files[name]=sha(p)
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),qualificationFields=19,finitePublicManifestReads=len(reads),normalClassFiles=len(classes),supplementalCandidateSources=len(rows),previousCandidateSources=87,unionCandidateSources=len(union),additionalCandidateNames=added,qualificationTransferred=False,allBase59Qualified=False,allCurrent93Qualified=False,questionFiveExistingWholeProofBound=True,questionComponentDelta=0,currentAggregateUnchanged=93,currentUniqueUnchanged=453,productTestsExecuted=0,productClassesInitialized=0,actualBackendActions=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,costLedgerObservedSha256=sha(ledger),normalManifestSha256=sha(normal),publicManifestReads=reads,declinedReferences=declines,files=files,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,qualificationFields=19,publicManifestReads=len(reads),supplementalNames=len(rows),unionNames=len(union),newCandidateNames=added,questionExisting5Replayed=0,manifestSha256=sha(O/'manifest.json'))))
