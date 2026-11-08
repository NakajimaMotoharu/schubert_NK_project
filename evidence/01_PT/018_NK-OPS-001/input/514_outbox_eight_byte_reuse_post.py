"""Independent byte CRC, XML and full physical closure; no report/Test regeneration."""
import copy,datetime,hashlib,json,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';I=B/'evidence/PG23736-outbox-eight-byte-reuse-v1';O=B/'evidence/PG23738-outbox-eight-byte-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert not O.exists();m=load(I/'manifest.json');cfg=load(R/m['config']['path']);assert sha(R/m['config']['path'])==m['config']['sha256'];
for n,pin in m['artifacts'].items():assert sha(I/n)==pin
for n,pin in cfg['publicInputFiles'].items():assert sha(R/n)==pin
old=B/'evidence/provisional/PG9756-outbox-value-post-v3';oldm=load(old/'manifest.json');counter=load(old/'whole-module-counters.json');current=load(Path(cfg['currentNormalManifest']['path']));jar=Path(current['jars']['api']['path']);assert sha(jar)==current['jars']['api']['sha256'];rows=load(I/'class-bindings.json');sources=load(I/'source-bindings.json');tests=load(I/'test-bindings.json');index=load(B/'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json')
def crc(data):
 value=0
 for byte in data:
  value ^= byte
  for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
 return f'{value:016x}'
def valid(r,summary):
 assert len(r)==len({x['physicalClass'] for x in r})==8
 assert {x['physicalClass'] for x in r}==set(oldm['physicalClassHashes'])
 assert summary['actualTestsExecuted']==summary['newUniqueTests']==summary['newAcceptance']==0
 assert summary['currentTestExecutionQualified'] is False and summary['newMeasuredCoverage'] is False
 assert all(all(x['missed']==0 for x in row['counters'].values()) for row in r)
 for row in r:
  n=row['physicalClass'];assert row['sha256']==index[n]['sha256']==oldm['physicalClassHashes'][n] and row['crc64']==index[n]['crc64']==counter['physicalClasses'][n]['crc64']
valid(rows,m)
with zipfile.ZipFile(jar) as z:
 for row in rows:
  raw=z.read(row['physicalClass']+'.class');assert crc(raw)==row['crc64'] and hashlib.sha256(raw).hexdigest()==row['sha256']
assert set(sources)=={x['mainPath'] for x in rows} and {k for k,v in index.items() if v['path'] in sources}=={x['physicalClass'] for x in rows}
for n,v in sources.items():assert sha(R/n)==v['sha256']==cfg['currentSourceFiles'][n] and v['currentAndOriginalBytesIdentical']
assert sum(v['currentBytesIdenticalToOriginal'] for v in tests.values())==2 and len(tests)==4 and all(v['currentTestExecuted'] is False for v in tests.values())
for n,v in tests.items():assert sha(R/n)==v['currentSha256']==cfg['currentTestSources'][n]
actual=[]
for n,pin in oldm['xmlHashes'].items():
 raw=(old/n).read_bytes();assert hashlib.sha256(raw).hexdigest()==pin;suite=ET.fromstring(raw);assert suite.tag=='testsuite';assert all(int(suite.get(k,0))==0 for k in ['failures','errors','skipped']);xs=suite.findall('testcase');assert len(xs)==int(suite.get('tests'))
 for x in xs:assert not list(x);actual.append((x.get('classname'),x.get('name')))
assert len(actual)==len(set(actual))==13 and oldm['actualTests']==13 and oldm['suites']==4 and oldm['coverageUnion'] is False
negative=0
for kind in ['MISSING_CLASS','DUPLICATE_CLASS','BAD_HASH','BAD_CRC','MISSED_BRANCH','FALSE_CURRENT_TEST','NEW_TEST_INCREMENT']:
 rs=copy.deepcopy(rows);summary=dict(m)
 if kind=='MISSING_CLASS':rs.pop()
 elif kind=='DUPLICATE_CLASS':rs[-1]=rs[0]
 elif kind=='BAD_HASH':rs[0]['sha256']='0'*64
 elif kind=='BAD_CRC':rs[0]['crc64']='0'*16
 elif kind=='MISSED_BRANCH':rs[0]['counters']['BRANCH']['missed']=1
 elif kind=='FALSE_CURRENT_TEST':summary['currentTestExecutionQualified']=True
 else:summary['newUniqueTests']=13
 try:valid(rs,summary)
 except AssertionError:negative+=1
 else:raise AssertionError('metadata negative not rejected')
assert negative==7
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],currentCoreMain=m['currentCoreMain'],originalSource=m['originalSource'],producer=dict(path=str((I/'manifest.json').relative_to(R)),sha256=sha(I/'manifest.json')),status=m['status'],currentNormalPhysicalClasses=8,completeSourceFileClosures=8,directByteCrcChecks=8,oldXmlTestsVerified=13,oldXmlSuites=4,oldCounters=m['originalCounters'],actualTestsExecuted=0,newUniqueTests=0,newAcceptance=0,currentTestSourceMatches=2,currentTestSourceDifferences=2,currentTestExecutionQualified=False,newMeasuredCoverage=False,metadataNegativeChecks=negative,oldOrCurrentCoverageUnion=False,whole451Accepted=False,formalUpdated=False,effortRate=None,actualBackendActions=0,javaCompilerOrMainOrTestExecuted=False,protectedPathsRead=False,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,classes=8,originalTests=13,newTests=0,metadataNegatives=negative,manifestSha256=sha(O/'manifest.json'))))
