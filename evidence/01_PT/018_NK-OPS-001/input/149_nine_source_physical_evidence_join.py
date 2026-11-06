"""Read SourceFile metadata and immutable original receipts; never load Product classes."""
from pathlib import Path
import collections,datetime,hashlib,json,subprocess,zipfile
import xml.etree.ElementTree as ET

def source_file(data):
 assert data[:4]==bytes.fromhex('cafebabe');pos=8;pool={}
 def u2():
  nonlocal pos
  n=int.from_bytes(data[pos:pos+2],'big');pos+=2;return n
 count=u2();i=1
 while i<count:
  tag=data[pos];pos+=1
  if tag==1:n=u2();pool[i]=data[pos:pos+n];pos+=n
  elif tag in (3,4):pos+=4
  elif tag in (5,6):pos+=8;i+=1
  elif tag in (7,8,16,19,20):pos+=2
  elif tag in (9,10,11,12,17,18):pos+=4
  elif tag==15:pos+=3
  else:raise ValueError('unknown class constant tag')
  i+=1
 pos+=6;interfaces=u2();pos+=2*interfaces
 for _ in range(2):
  count=u2()
  for _ in range(count):
   pos+=6;attrs=u2()
   for _ in range(attrs):pos+=2;n=int.from_bytes(data[pos:pos+4],'big');pos+=4+n
 result=None;attrs=u2()
 for _ in range(attrs):
  name=u2();n=int.from_bytes(data[pos:pos+4],'big');pos+=4
  if pool[name]==b'SourceFile':assert n==2 and result is None;result=pool[int.from_bytes(data[pos:pos+2],'big')].decode('ascii')
  pos+=n
 assert pos==len(data);return result

r=Path.cwd();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
matrixp=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21866-current-changed25-pg-pt-evidence-matrix-v1/manifest.json';assert sha(matrixp)=='aaf804e3295cb6afe5404f03ba496784b5db7e396a8d096fdb7406078d089b64';matrix=load(matrixp)
statuses={'SAME_BYTE_COUNTER_CANDIDATE_SCOPE_JOIN_PENDING','HISTORICAL_WHOLE_FACT_CURRENT_JOIN_PENDING','CURRENT_CLASS_HISTORICAL_RECEIPT_METADATA_BOUND'};targets=[x for x in matrix['rows'] if x['status'] in statuses];assert len(targets)==9
normalp=r.parent/'pgpt-runs/PG379/pg20990-outbox-required-six-main-compile-v1/manifest.safe.json';toolp=r.parent/'pgpt-runs/PG379/pg21088-characterization-tool-original-main-compile-v1/manifest.safe.json';normal,tool=load(normalp),load(toolp);assert sha(normalp)=='1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618' and sha(toolp)=='068773debc310f76f580ef1eea8de2e5735cada128d2e6c677ce62ebdffd2e0a'
special={'TargetAdapter':'evidence/01_PT/020_NK-CHR-001/evidence/PG18716-gate-definitions-thirtyfive-v1/manifest.json','JmsMessageGuard':'evidence/01_PT/005_NK-MSG-001/evidence/provisional/PG18644-jms-uuid-normal-post-v1/manifest.json'}
rows=[];originals={};pending=[]
for row in targets:
 n=row['path'];simple=Path(n).stem;relative=n.split('/src/main/java/',1)[1];pkg=relative.rsplit('/',1)[0];filename=Path(n).name
 istool=n.startswith('program/');module=None if istool else n.split('/')[1].removeprefix('schubert-nk-');nm=tool if istool else normal;jar=tool['jar'] if istool else normal['jars'][module];assert sha(Path(jar['path']))==jar['sha256'];assert sha(r/n)==nm['begin']['inputHashes'][n]==row['sha256']
 current={}
 with zipfile.ZipFile(jar['path']) as z:
  for name in z.namelist():
   if name.endswith('.class') and name.rsplit('/',1)[0]==pkg:
    data=z.read(name)
    if source_file(data)==filename:
     cls=name[:-6];h=hashlib.sha256(data).hexdigest();expected=tool['physicalHashes'][cls] if istool else normal['normalPhysicalClassHashes'][module+':'+name];assert h==expected;current[cls]=h
 assert current
 choices=[special[simple]] if simple in special else [x['path'] for x in row['evidenceRefs'] if x['path'].endswith('/manifest.json')]
 # Several historical receipts may exist; inspect newest named candidate first, without replay.
 proof_rows=[]
 for choice in reversed(choices):
  oldp=r/choice;old=load(oldp)
  if old.get('actualExit')!=0:continue
  oldphysical=old.get('physicalHashes') or old.get('physicalClassHashes') or {k:v['normalClassSha256'] for k,v in old.get('sourceUnits',{}).items()}
  if not all(oldphysical.get(k)==h for k,h in current.items()):continue
  if hashlib.sha256(subprocess.check_output(['git','show',old['source']+':'+n])).hexdigest()!=row['sha256']:continue
  xmlname=next((x for x in ['coverage.xml','jacoco.xml'] if x in old.get('files',{})),None)
  if xmlname is None:continue
  xmlp=oldp.parent/xmlname;assert sha(xmlp)==old['files'][xmlname];xml=ET.parse(xmlp)
  sources=[x for x in xml.findall('.//sourcefile') if x.get('name')==filename];assert len(sources)==1
  cs={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in sources[0].findall('counter')}
  if not all(k in cs and cs[k]['missed']==0 and cs[k]['covered']>0 for k in ['LINE','METHOD','CLASS']):continue
  if 'BRANCH' in cs and cs['BRANCH']['missed']!=0:continue
  allclasses={c.get('name'):c for c in xml.findall('.//class')};assert set(current)<=set(allclasses)
  for cls in current:
   for count in allclasses[cls].findall('counter'):assert int(count.get('missed'))==0
  originals[choice]=dict(sha256=sha(oldp),source=old['source'],tests=old.get('tests'),originalExit=0)
  proof_rows.append(dict(path=choice,sha256=sha(oldp),source=old['source'],originalTests=old.get('tests'),sourceFileCounters=cs,coverageXml=dict(path=str(xmlp.relative_to(r)),sha256=sha(xmlp)),physicalFamily=current,originalScopeNotReplayed=True));break
 if not proof_rows:pending.append(n)
 rows.append(dict(path=n,owner=row['owner'],costOwner=row['costOwner'],mainSha256=row['sha256'],normalJar=jar,normalSource=nm['source'],physicalFamily=current,proofs=proof_rows,status='CURRENT_BYTE_SOURCE_FAMILY_AND_HISTORICAL_WHOLE_COUNTERS_BOUND' if proof_rows else 'PENDING_SOURCE_SCOPE_OR_BYTE_COUNTER_JOIN',currentDependencyWholeQualificationTransferred=False,newLeafAccepted=False,newProductTests=0))
spec=r/'evidence/01_PT/018_NK-OPS-001/3618_現九source全physical原証拠一括結合仕様.md'
for p in [spec,Path(__file__)]:assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(p.relative_to(r))])).hexdigest()==sha(p)
out=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21878-current-nine-source-physical-evidence-join-v1';assert not out.exists();out.mkdir()
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=head,productionCoreMain=normal['source'],matrix=dict(path=str(matrixp.relative_to(r)),sha256=sha(matrixp)),rows=rows,statusCounts=dict(collections.Counter(x['status'] for x in rows)),boundSources=9-len(pending),pendingSources=pending,distinctOriginalRuns=originals,physicalSourceFileAttributeUsed=True,productClassExtractionPerformed=False,currentDependencyWholeQualificationTransferred=False,newProductTests=0,newMethods=0,newSourceProofs=0,newAcceptance=0,wholeG13Accepted=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,targets=9,boundSources=v['boundSources'],pendingSources=pending,manifestSha256=sha(out/'manifest.json'))))
