"""Qualify exact old source/physical/counter evidence without re-running63 tests."""
from pathlib import Path
import datetime,hashlib,json,subprocess,zipfile
import xml.etree.ElementTree as ET

def class_flags(data):
 assert data[:4]==bytes.fromhex('cafebabe');count=int.from_bytes(data[8:10],'big');pos=10;index=1
 while index<count:
  tag=data[pos];pos+=1
  if tag==1:length=int.from_bytes(data[pos:pos+2],'big');pos+=2+length
  elif tag in (3,4):pos+=4
  elif tag in (5,6):pos+=8;index+=1
  elif tag in (7,8,16,19,20):pos+=2
  elif tag in (9,10,11,12,17,18):pos+=4
  elif tag==15:pos+=3
  else:raise ValueError('unknown class constant tag')
  index+=1
 return int.from_bytes(data[pos:pos+2],'big')

r=Path.cwd();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
p=r/'evidence/01_PT/002_NK-PRO-002/evidence/PG21852-current-protocol-four-source-existing-proof-trace-v1/manifest.json';assert sha(p)=='e8f0410b782cea881f4ca94927e173bf010c0c0583d18f1916b92e0552c22ebe';m=load(p);assert m['actualExit']==0 and len(m['rows'])==4 and len(m['physicalHashes'])==7 and not m['currentCombinedRun']
oldp=r/m['original']['path'];assert sha(oldp)==m['original']['sha256'];old=load(oldp);indp=r/m['originalIndependentPost']['path'];assert sha(indp)==m['originalIndependentPost']['sha256'];ind=load(indp)
assert old['actualExit']==old['failures']==old['errors']==old['skipped']==ind['aborted']==0 and old['tests']==ind['tests']==63
normalp=Path(m['normalManifest']['path']);assert sha(normalp)==m['normalManifest']['sha256'];normal=load(normalp);jar=m['normalProtocolJar'];assert normal['jars']['protocol']==jar and sha(Path(jar['path']))==jar['sha256']
with zipfile.ZipFile(jar['path']) as z:
 flags={}
 for cls,h in m['physicalHashes'].items():
  data=z.read(cls+'.class');assert hashlib.sha256(data).hexdigest()==h==old['physicalHashes'][cls]==normal['normalPhysicalClassHashes']['protocol:'+cls+'.class'];flags[cls]=class_flags(data)
 for cls in m['compilerSyntheticDefaultFiltered']:assert flags[cls]&0x1000
assert set(m['compilerSyntheticDefaultFiltered'])==set(ind['compilerSyntheticNoCode']) and len(m['compilerSyntheticDefaultFiltered'])==2
tree=ET.parse(oldp.parent/'jacoco.xml');classes={c.get('name') for c in tree.findall('.//class')};assert classes==set(m['physicalHashes'])-set(m['compilerSyntheticDefaultFiltered'])
totals={k:0 for k in ['LINE','METHOD','CLASS','BRANCH']}
for row in m['rows']:
 n=row['path'];assert sha(r/n)==row['mainSha256']==old['inputHashes'][n]==normal['begin']['inputHashes'][n] and row['owner']==row['costOwner']
 src=next(s for s in tree.findall('.//sourcefile') if s.get('name')==Path(n).name);cs={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in src.findall('counter')};assert cs==row['originalSourceFileCounters']
 for k in ['LINE','METHOD','CLASS']:assert cs[k]['missed']==0
 if 'BRANCH' in cs:assert cs['BRANCH']['missed']==0
 for k in totals:totals[k]+=cs.get(k,{}).get('covered',0)
assert totals==m['sourcefileCounterTotal']==dict(LINE=661,METHOD=89,CLASS=5,BRANCH=400)
pairs=[]
for filename in ['TEST-junit-jupiter.xml','TEST-junit-vintage.xml','TEST-junit-platform-suite.xml']:
 assert sha(oldp.parent/filename)==old['files'][filename]
 for t in ET.parse(oldp.parent/filename).getroot().iter('testcase'):
  assert not any(t.find(n) is not None for n in ['failure','error','skipped']);pairs.append([t.get('classname'),t.get('name','').removesuffix('()')])
assert len(pairs)==63 and {tuple(x) for x in pairs}=={tuple(x) for x in m['originalTestMethods']}
ref=m['originalOracleSpecification'];assert sha(r/ref['path'])==ref['sha256']
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(Path(__file__).relative_to(r))])).hexdigest()==sha(Path(__file__))
out=r/'evidence/01_PT/002_NK-PRO-002/evidence/PG21854-current-protocol-trace-independent-post-v1';assert not out.exists();out.mkdir()
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),checkerSource=head,checkerSha256=sha(Path(__file__)),observerSource=m['observerSource'],productionCoreMain=m['productionCoreMain'],original=dict(path=str(p.relative_to(r)),sha256=sha(p)),boundSources=4,boundPhysicalClasses=7,defaultCompilerSyntheticClasses=2,sourceCounterTotals=totals,historicalTestsReferenced=63,newProductTests=0,newMethods=0,newSourceProofs=0,newAcceptance=0,currentCombinedRun=False,singleTestProbeAttributionMeasured=False,wholeG13Accepted=False,whole451Accepted=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sources=4,physicalClasses=7,newProductTests=0,manifestSha256=sha(out/'manifest.json'))))
