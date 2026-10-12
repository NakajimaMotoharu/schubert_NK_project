"""Independent exact fresh XML/source/coverage/static qualification, not whole acceptance."""
import hashlib
import json
import os
from pathlib import Path
from lan_server import run

W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
CODE=r'''
import datetime,hashlib,json,xml.etree.ElementTree as E,zipfile
from pathlib import Path
BASE=Path('/home/mini/schubert-nk-pgpt');SOURCE=BASE/'source-selected-PG1530';OUT=BASE/'runs/PG1530-selected-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(v):
 if not v:raise ValueError('independent selected source/XML/counter qualification refused')
manifest=json.loads((OUT/'manifest.safe.json').read_bytes());begin=json.loads((OUT/'begin.safe.json').read_bytes())
require(manifest['actualExit']==manifest['mavenExit']==0 and manifest['sourceSnapshot']==begin['sourceSnapshot']=='4d6bcbddb417b76d27e52d5d9640752c300edccf')
require(manifest['sourceInputsUnchanged']is True and all(sha(SOURCE/p)==h for p,h in begin['inputs'].items()))
require(begin['compileOnlyUnselectedModules']==[])
expected={'LinuxFilesystemClassifierTest':5,'ResourceScopeTest':8,'LinuxInodeSecurityTest':9};require(begin['expectedSuites']==expected and set(manifest['suites'])==set(expected))
start=datetime.datetime.fromisoformat(begin['startUTC']).timestamp()*1e9;end=datetime.datetime.fromisoformat(manifest['endUTC']).timestamp()*1e9
target=SOURCE/'src/schubert-nk-storage/target';count=0;xmlhash={}
for name,n in expected.items():
 paths=list((target/'surefire-reports').glob('TEST-*.'+name+'.xml'));require(len(paths)==1);p=paths[0];x=E.parse(p).getroot();cases=x.findall('testcase')
 require(int(x.attrib['tests'])==len(cases)==n and all(int(x.attrib[k])==0 for k in ['failures','errors','skipped']))
 require(len({c.attrib['name']for c in cases})==n and not any(c.find(k)is not None for c in cases for k in ['failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError']))
 require(start<=p.stat().st_mtime_ns<=end and sha(p)==manifest['suites'][name]['xmlSha256']);count+=n;xmlhash[name]=sha(p)
spot=target/'spotbugsXml.xml';require(len(E.parse(spot).getroot().findall('.//BugInstance'))==0 and manifest['staticIssues']=={'storage':0})
xml=target/'site/jacoco/jacoco.xml';tree=E.parse(xml).getroot();nodes=[c for c in tree.findall('.//class')if c.attrib['name']=='dev/codex/schubert/nk/storage/LinuxFilesystemClassifier'];require(len(nodes)==1)
counters={c.attrib['type']:{k:int(c.attrib[k])for k in ['covered','missed']}for c in nodes[0].findall('counter')}
require(all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS','BRANCH'])and counters==manifest['classifierCoverage'][nodes[0].attrib['name']])
interfaces=[c for c in tree.findall('.//class')if c.attrib['name']=='dev/codex/schubert/nk/storage/LinuxFilesystemClassifier$StatfsCall'];require(len(interfaces)==1 and not interfaces[0].findall('counter'))
jar=target/'schubert-nk-storage-0.1.0-SNAPSHOT.jar'
with zipfile.ZipFile(jar)as z:
 classes={n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
 require(set(classes)=={str(p.relative_to(target/'classes'))for p in(target/'classes').rglob('*.class')})
 require(all(h==sha(target/'classes'/n)for n,h in classes.items()))
print(json.dumps({'actualExit':0,'sourceSnapshot':manifest['sourceSnapshot'],'tests':count,'suites':3,'FESflakyNotRun':0,'staticIssues':0,'classifierFourCounters100':True,'counters':counters,'declarationInterfaceNoExecutableCounters':True,'sourceInputsUnchanged':True,'xmlHashes':xmlhash,'mainClasses':len(classes),'jarSha256':sha(jar),'coverageXmlSha256':sha(xml),'execSha256':sha(target/'jacoco.exec'),'manifestSha256':sha(OUT/'manifest.safe.json'),'startUTC':begin['startUTC'],'endUTC':manifest['endUTC'],'elapsedSeconds':manifest['elapsedSeconds'],'formalAccepted':False,'wholeAccepted':False}))
'''
def main():
 os.umask(0o077);out=W/'pg1531-filesystem-selected-qualified-v1';out.mkdir(mode=0o700)
 compile(CODE,'<independent source and four-counter qualification>','exec')
 code,status=run("python3 - <<'PG1531'\n"+CODE+"\nPG1531",timeout=60)
 (out/'observer.private.log').write_text(status)
 v={'actualExit':code,'qualificationSourceSha256':hashlib.sha256(CODE.encode()).hexdigest(),'formalAccepted':False}
 if code==0:
  line=next(s for s in status.splitlines()if s.strip().startswith('{'));v['result']=json.loads(line)
 with(out/'manifest.safe.json').open('x')as f:json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 print(json.dumps(v));return code
if __name__=='__main__':raise SystemExit(main())
