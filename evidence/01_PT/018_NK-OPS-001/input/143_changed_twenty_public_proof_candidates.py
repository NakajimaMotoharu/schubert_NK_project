from pathlib import Path
import json,hashlib,subprocess,datetime,collections
from pgpt_program_proof_lookup import candidate,HELD_NAMES
r=Path.cwd();runs=r.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seedpath=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21766-current4217-static-artifact-lineage-v2/changed-artifacts.json';seed=load(seedpath);targets=[dict(path=x['path'],owner=x['owner'],evidenceStatus='CHANGED_JAVA_REQUIRES_INDIVIDUAL_PROOF_JOIN') for x in seed if x['kind']=='JAVA'];assert len(targets)==20 and len({x['path'] for x in targets})==20
normalpath=runs/'pg20990-outbox-required-six-main-compile-v1/manifest.safe.json';toolpath=runs/'pg21088-characterization-tool-original-main-compile-v1/manifest.safe.json';assert sha(normalpath)=='1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618' and sha(toolpath)=='068773debc310f76f580ef1eea8de2e5735cada128d2e6c677ce62ebdffd2e0a';normal=load(normalpath);tool=load(toolpath);assert normal['actualExit']==tool['actualExit']==0
spec=r/'evidence/01_PT/018_NK-OPS-001/3612_現4217変更二十Java既存証拠候補抽出仕様.md';assert spec.is_file()
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
for p in [spec,Path(__file__)]:assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(p.relative_to(r))])).hexdigest()==sha(p)
seedmanifest=load(seedpath.parent/'manifest.json');assert sha(seedpath.parent/'manifest.json')=='ee465df2a40a6bba40c02680062a2cbc7d0441a0bc012c67efebfb752ac70a09' and sha(seedpath)==seedmanifest['files']['changed-artifacts.json']
scopes=[(normal,'src/**/src/main/java/**/*.java'),(tool,'program/characterization/src/main/java/**/*.java')]
for m,pattern in scopes:
 assert subprocess.run(['git','diff','--quiet',m['source'],'--',pattern]).returncode==0
 assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--',pattern]).strip()
hashes={**normal['begin']['inputHashes'],**tool['begin']['inputHashes']};by_name=collections.defaultdict(list);rows={}
for x in targets:
 path=x['path'];assert Path(path).name not in HELD_NAMES and '/src/main/java/' in path and path in hashes;h=hashes[path];assert isinstance(h,str) and len(h)==64
 by_name[Path(path).stem].append(path);rows[path]=dict(path=path,originalStatus=x['evidenceStatus'],canonicalOwner=x['owner'],normalMainSha256=h,candidates=[])
names=subprocess.check_output(['git','ls-files','-z','--','evidence/01_PT']).decode().split('\0');unread=[];unsupported=[];scanned=0
for name in names:
 if not name.endswith('/manifest.json') or '.private.' in name or any(x in HELD_NAMES for x in Path(name).parts):continue
 p=r/name
 if p.is_symlink() or not p.is_file() or p.stat().st_size>2*1024*1024:unread.append(name);continue
 data=p.read_bytes();present=[n for n in by_name if n.encode() in data]
 if not present:continue
 scanned+=1
 try:v=json.loads(data)
 except (ValueError,UnicodeDecodeError) as e:unsupported.append(dict(path=name,reasonType=type(e).__name__));continue
 if not isinstance(v,dict):continue
 for name_key in present:
  for source_path in by_name[name_key]:
   try:item=candidate(v,name_key,hashes[source_path])
   except (ValueError,TypeError,AttributeError,KeyError) as e:unsupported.append(dict(path=name,className=name_key,reasonType=type(e).__name__));continue
   if item is None or item['mainPath']!=source_path:continue
   refs=dict(path=name,sha256=hashlib.sha256(data).hexdigest(),**item);rows[source_path]['candidates'].append(refs)
for row in rows.values():
 vals=row['candidates'];same=[x for x in vals if x['currentMainByteEqual'] and x['originalExit']==0];full=[x for x in same if x['allFourMissedZero'] or (x['lineMethodClassMissedZero'] and x['branchAssessment']=='EXPLICIT_NATURAL_ZERO_NOT_BRANCH100')]
 row['candidateStatus']='SAME_BYTE_SUCCESS_COUNTER_CANDIDATE' if full else 'SAME_BYTE_PARTIAL_CANDIDATE' if same else 'HISTORICAL_OR_FAILED_CANDIDATE' if vals else 'NO_SUPPORTED_SCHEMA_CANDIDATE_NOT_PROOF_OF_ABSENCE'
 row['wholeSourceQualificationTransferred']=False
counts=dict(collections.Counter(x['candidateStatus'] for x in rows.values()));out=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21792-current4217-changed-twenty-proof-candidates-v1';assert not out.exists();out.mkdir();now=datetime.datetime.now().astimezone().isoformat();value=dict(atJST=now,actualExit=0,source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),classification='PUBLIC_METADATA_CANDIDATE_DISCOVERY_ONLY',seed=dict(path=str(seedpath),sha256=sha(seedpath)),normalManifests=[dict(path=str(p),sha256=sha(p)) for p in [normalpath,toolpath]],currentMainUnchangedProvenByGitScopes=[s for m,s in scopes],latestPriorCurrentJavaInputVerification=dict(path='evidence/01_PT/018_NK-OPS-001/evidence/PG21768-current4217-static-lineage-independent-post-v1/manifest.json',sha256='c257842b1081b74e5f6860f72c2c722cc905346a75f0a2f5d6475571024631b4'),parser=dict(path='tools/quality/pgpt_program_proof_lookup.py',sha256=sha(r/'tools/quality/pgpt_program_proof_lookup.py')),targetCount=20,resourceRowsNotInJavaLookup=3,matchingBoundedManifestCount=scanned,statusCounts=counts,unreadBoundedManifests=unread,unsupported=unsupported,rows=list(rows.values()),productTestsExecuted=0,newSourceProofs=0,newAcceptance=0,formalUpdated=False,effortRate=None,limits='Candidate discovery only. Counter receipt may cover a named class, not all nested physical classes of the source. Original case/source/run/CRC/static/safety/criteria require independent qualification before any transfer. No absence, acceptance or permission inference. No old successes replayed, private/raw/VM/DB/Root/archive reads or held filenames accessed.')
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,targets=20,statusCounts=counts,unsupported=len(unsupported),unread=len(unread),productTests=0,manifestSha256=sha(out/'manifest.json'))))
