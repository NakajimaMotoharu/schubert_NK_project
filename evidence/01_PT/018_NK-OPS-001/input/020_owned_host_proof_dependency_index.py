"""Public host-only proof index; static bytes/metadata, no Product execution or acceptance."""
from pathlib import Path
import json,hashlib,sys,re,subprocess,zipfile,datetime,shutil,collections,functools
ROOT=Path.cwd();RUNS=ROOT.parent/'pgpt-runs/PG379';NORMAL=RUNS/'pg19740-f03-index-style-six-main-compile-v1';SLOT=RUNS/'pg19800-host-qualified-proof-index-v1';PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/PG19800-host-qualified-proof-index-v1';SOURCE='28af318d0198fe7432ca6fcd234d3fabbfd10173';PROGRAMS=['002_NK-PRO-002','005_NK-MSG-001','007_NK-AUT-001','008_NK-SCN-001','009_NK-MED-001','010_NK-ADM-001','011_NK-QST-001','014_NK-QRY-001','015_NK-WEB-001','016_NK-WEB-002','017_NK-BAT-001','020_NK-CHR-001'];HELD={'dev/codex/schubert/nk/api/error/TemporaryInfrastructureException','dev/codex/schubert/nk/web/bootstrap/WebStartupException','dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing','dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
TABLE=[]
for number in range(256):
 value=number
 for bit in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
 TABLE.append(value)
def crc(data):
 assert data[:4]==b'\xca\xfe\xba\xbe' and int.from_bytes(data[6:8],'big')==69
 value=0
 for octet in data:value=(value>>8)^TABLE[(value^octet)&255]
 return f'{value:016x}'

@functools.lru_cache(None)
def blob(ref,path):
 assert re.fullmatch('[0-9a-f]{40}',ref) or ref=='HEAD'
 assert path.startswith('src/') and '/src/test/java/' in path and not any(s in path for s in ['RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest'])
 result=subprocess.run(['git','rev-parse',ref+':'+path],text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=False)
 return result.stdout.strip() if result.returncode==0 else None

@functools.lru_cache(None)
def changed(ref):
 if not isinstance(ref,str) or not re.fullmatch('[0-9a-f]{40}',ref):return None
 result=subprocess.run(['git','diff','--name-only',ref,SOURCE,'--','src'],text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=False)
 return sorted(p for p in result.stdout.splitlines() if '/src/main/' in p) if result.returncode==0 else None

def collect():
 assert sha(NORMAL/'manifest.safe.json')=='45fa13f0a99583a03cb765e2c0ce05d94bd9d9adeadd89187ff3334c58f31d8b';normal=json.loads((NORMAL/'manifest.safe.json').read_text());assert normal['actualExit']==0 and normal['source']==SOURCE
 assert all(sha(ROOT/p)==h for p,h in normal['begin']['inputHashes'].items());classes={};jars={}
 for role,item in normal['jars'].items():
  assert sha(item['path'])==item['sha256'];jars[role]=item['sha256']
  with zipfile.ZipFile(item['path']) as jar:
   for name in jar.namelist():
    if name.endswith('.class'):
     data=jar.read(name);key=name[:-6];classes.setdefault(key,[]).append({'module':role,'sha256':hashlib.sha256(data).hexdigest(),'crc':crc(data)})
 # Independent saved JaCoCo classinfo ID proves the index CRC interpretation, not Product behavior.
 witness=ROOT/'evidence/01_PT/007_NK-AUT-001/evidence/PG19788-session-audit-nine-v1/manifest.json';wm=json.loads(witness.read_text());assert all(any(c['crc']==v for c in classes[k]) for k,v in wm['physicalClassIds'].items());candidates=[];rejected=[]
 for program in PROGRAMS:
  for path in sorted((ROOT/'evidence/01_PT'/program/'evidence').glob('PG*/manifest.json')):
   label=path.parent.name.lower()
   if any(term in label for term in ['vm','native','root','cohort','history','failed','provisional','deployment','activation']):continue

   if path.is_symlink() or path.parent.is_symlink():continue
   m=json.loads(path.read_text());why=[]
   if type(m.get('actualExit')) is not int or m['actualExit']!=0 or type(m.get('tests')) is not int or m['tests']<=0:continue
   if m.get('onlyMemoryCallbackFixtures') is not True or m.get('oldExecUnion') is not False or m.get('manualCoverageExclusions')!=[]:continue
   if any(type(m.get(k)) is not int or m[k]!=0 for k in ['failures','errors','skipped','aborted']):continue
   hits=m.get('heldFourProbeHits');cov=m.get('coverage');physical=m.get('physicalHashes');sourcehash=m.get('inputHashes');session=m.get('session')
   if not isinstance(hits,dict) or set(hits)!=HELD or any(type(v) is not int or v!=0 for v in hits.values()):continue
   if not isinstance(cov,dict) or not cov or not isinstance(physical,dict) or not physical or not isinstance(sourcehash,dict) or not isinstance(session,str) or not session:continue
   if any(any(k==h or k.startswith(h+'$') for h in HELD) for k in cov):continue
   if not isinstance(m.get('wholeSourceFourCounter100'),list) or not m['wholeSourceFourCounter100']:continue
   if not all(isinstance(row,dict) and all(isinstance(row.get(k),dict) and all(type(row[k].get(v)) is int and row[k][v]>=0 for v in ['covered','missed']) for k in ['LINE','METHOD','CLASS','BRANCH']) for row in cov.values()):continue
   counters={key:{'covered':sum(row.get(key,{}).get('covered',0) for row in cov.values()),'missed':sum(row.get(key,{}).get('missed',0) for row in cov.values())} for key in ['LINE','METHOD','CLASS','BRANCH']}
   if not all(isinstance(v,int) and not isinstance(v,bool) and v>=0 for r in counters.values() for v in r.values()) or any(r['missed']!=0 for r in counters.values()) or any(counters[k]['covered']<=0 for k in ['LINE','METHOD','CLASS']):continue
   files=m.get('files',{});execpath=path.parent/'execinfo.stdout'
   if not isinstance(files,dict) or files.get('execinfo.stdout')!=sha(execpath):raise AssertionError('public saved exec metadata missing or hash mismatch')
   used={}
   for line in execpath.read_text().splitlines():
    match=re.fullmatch(r'([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(dev/codex/schubert/nk/[^\s]+)',line.strip())
    if match:
     key=match.group(4);used.setdefault(key,set()).add(match.group(1))
   assert used and all(len(ids)==1 for ids in used.values())
   byte_matches={k:bool(k in classes and any(v['sha256']==h for v in classes[k])) for k,h in physical.items()}
   mainrows=[];tests=[]
   for name,h in sourcehash.items():
    if name.startswith('src/') and '/src/main/java/' in name:
     prefix=name.split('/src/main/java/',1)[1][:-5]
     if any(prefix==held for held in HELD):raise AssertionError('held target cannot enter component index')
     mainrows.append({'path':name,'savedSha256':h,'currentShaMatches':name in normal['begin']['inputHashes'] and normal['begin']['inputHashes'][name]==h})
    elif name.startswith('src/') and '/src/test/java/' in name:
     if any(s in name for s in ['RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest']):raise AssertionError('forbidden Test body not read')
     old=blob(m['source'],name);current=blob('HEAD',name);tests.append({'path':name,'savedSource':m['source'],'savedGitBlob':old,'currentGitBlob':current,'sameTrackedBytes':old is not None and old==current,'bodyNotRead':True})
   if not mainrows or not tests:
    rejected.append({'manifest':str(path.relative_to(ROOT)),'reason':'Outside supported six-Main src/recorded Test schema; e.g. separate Characterization source, not accepted here.'});continue
   drift=[{'class':k,'savedClassId':next(iter(ids)),'currentClassIds':sorted({v['crc'] for v in classes[k]})} for k,ids in used.items() if k in classes and not any(v['crc'] in ids for v in classes[k])];missing=[k for k in used if k not in classes and not '/src/test/' in k];delta=changed(m.get('productionCoreMain'));currentstatus='TARGET_OR_TEST_CHANGED' if not all(byte_matches.values()) or not all(r['currentShaMatches'] for r in mainrows) or not all(r['sameTrackedBytes'] for r in tests) else 'OBSERVED_CURRENT_CORE_DEPENDENCY_DRIFT' if drift else 'SAVED_USED_CORE_CLASS_IDS_MATCH_CURRENT'
   candidates.append({'manifest':str(path.relative_to(ROOT)),'manifestSha256':sha(path),'source':m['source'],'savedCore':m.get('productionCoreMain'),'tests':m['tests'],'session':session,'countersAtSavedRun':counters,'mainSources':mainrows,'testGitBlobBindings':tests,'physicalShaMatchCurrent':byte_matches,'savedUsedCoreClasses':sum(k in classes for k in used),'observedCoreClassIdDrift':drift,'unmappedProjectClassNamesIncludingOwnTestAndAux':sorted(missing),'savedCoreToCurrentMainPathsChanged':delta,'currentStatus':currentstatus,'currentScopeQualified':False,'newTestsExecuted':0,'formalAccepted':False,'qualificationNote':'Index binds existing target/test bytes and actually observed normal-core IDs only. Unobserved branches/dependencies, changed resources, SDK/native environment or old Source/test oracle applicability still require explicit impact review; no automatic source/run transfer or old exec union.'})
 return {'normalMainSource':SOURCE,'normalManifestSha256':sha(NORMAL/'manifest.safe.json'),'normalJars':jars,'currentPhysicalClasses':sum(len(v) for v in classes.values()),'crcWitness':{'manifest':str(witness.relative_to(ROOT)),'sha256':sha(witness),'actualJaCoCoIdsMatched':True},'programsRead':PROGRAMS,'publicModernSchemaCandidates':candidates,'candidateCount':len(candidates),'unsupportedAfterBasicGuards':rejected,'statusCounts':dict(collections.Counter(v['currentStatus'] for v in candidates)),'noTestBodiesRead':True,'noPrivateRawRead':True,'productExecuted':False,'newTests':0,'newComponents':0,'newIndividualAccepted':0,'global451Accepted':False,'formalUpdated':False,'scopeCompleteForAllHistory':False,'otherLegacyBindingsRemainAtOriginal867AndOtherDocuments':True}

def run():
 assert not SLOT.exists() and not PUBLIC.exists();v=collect();SLOT.mkdir();(SLOT/'index.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');m={'actualExit':0,'atJST':datetime.datetime.now().astimezone().isoformat(),'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'driverSha256':sha(__file__),'indexSha256':sha(SLOT/'index.json'),'candidateCount':v['candidateCount'],'statusCounts':v['statusCounts'],'productExecuted':False,'newAcceptance':0,'formalUpdated':False};(SLOT/'manifest.safe.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'actualExit':0,'candidates':v['candidateCount'],'status':v['statusCounts']}))

def post():
 m=json.loads((SLOT/'manifest.safe.json').read_text());assert m['actualExit']==0 and m['driverSha256']==sha(__file__) and m['indexSha256']==sha(SLOT/'index.json');assert collect()==json.loads((SLOT/'index.json').read_text());assert not PUBLIC.exists();PUBLIC.mkdir(parents=True)
 for p in SLOT.iterdir():
  if p.is_file():shutil.copyfile(p,PUBLIC/p.name)
 out=dict(m,independentReconstruction=True,originalManifestSha256=sha(SLOT/'manifest.safe.json'),files={p.name:sha(p) for p in PUBLIC.iterdir() if p.is_file()});(PUBLIC/'manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'actualExit':0,'candidates':m['candidateCount'],'manifestSha256':sha(PUBLIC/'manifest.json')}))

if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ['run','post']
 if sys.argv[1]=='run':run()
 else:post()
