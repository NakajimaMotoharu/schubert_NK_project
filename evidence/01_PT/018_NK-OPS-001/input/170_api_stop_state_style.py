"""Changed API stop Main pair and whole Test style scan; no Product execution."""
from pathlib import Path
import datetime
import hashlib
import json
import xml.etree.ElementTree as E
import pg9666_pagination_static as c
r=Path.cwd();w=r.parent/'pgpt-runs/PG379';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
nm=load(w/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');assert nm['actualExit']==0
names=['src/schubert-nk-api/src/'+p+'/java/dev/codex/schubert/nk/api/bootstrap/'+n+'.java' for p,n in [('main','ApiStopBudget'),('main','ApiProcessLifetime'),('test','ApiStopBudgetTest')]]
for n in names[:2]:assert sha(r/n)==nm['begin']['inputHashes'][n]
old=r/'evidence/01_PT/006_NK-MSG-002/evidence/PG21012-outbox-null-oracle-static-v1';pmd=load(old/'pmd-begin.safe.json')['command'];cs=load(old/'checkstyle-begin.safe.json')['command'];slot=w/'pg22088-api-stop-state-style-v1';assert not slot.exists();slot.mkdir();c.SLOT=slot
listing=slot/'source-list.txt';listing.write_text(''.join(str(r/n)+'\n' for n in names));tc=r.parent/'toolchain';cp=':'.join([*[v['path'] for v in nm['jars'].values()],str(tc/'junit-platform-console-standalone-1.13.4.jar'),str(tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar')])
for flag,value in [('--file-list',str(listing)),('--report-file',str(slot/'pmd.xml')),('--aux-classpath',cp)]:pmd[pmd.index(flag)+1]=value
cs[cs.index('-o')+1]=str(slot/'checkstyle.xml');cs[-1]='@'+str(listing)
stages={'pmd':c.step('pmd',pmd,r,timeout=120),'checkstyle':c.step('checkstyle',cs,r,timeout=120)};findings=[]
for file,tag in [('pmd.xml','violation'),('checkstyle.xml','error')]:
 for f in E.parse(slot/file).getroot().iter():
  if f.tag.rsplit('}',1)[-1]!='file':continue
  for n in f:
   if n.tag.rsplit('}',1)[-1]==tag:findings.append(dict(tool=file,path=str(Path(f.get('name')).relative_to(r)),attributes=n.attrib,message=' '.join(''.join(n.itertext()).split())))
errors=[n.attrib for n in E.parse(slot/'pmd.xml').getroot().iter() if n.tag.rsplit('}',1)[-1] in ['error','configerror']];assert not errors and stages['pmd']['actualExit'] in [0,4] and stages['checkstyle']['actualExit'] in [0,1]
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=nm['source'],inputHashes={n:sha(r/n) for n in names},stages=stages,findings=findings,processingErrors=errors,status='RAW_FINDINGS_REQUIRE_INDIVIDUAL_REVIEW',productTestsExecuted=0);(slot/'raw-manifest.safe.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(rawCount=len(findings),findings=findings,rawExits={k:s['actualExit'] for k,s in stages.items()})))
