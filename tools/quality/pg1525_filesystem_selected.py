"""SSC269 fresh isolated storage/batch PT, no VM/deployed dependency writes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy,run

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
REMOTE='/home/mini/schubert-nk-pgpt'

SERVER=r'''
import datetime,hashlib,json,os,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
BASE=Path('/home/mini/schubert-nk-pgpt');SOURCE=BASE/'source-selected-PG1525';OUT=BASE/'runs/PG1525-selected-v1'
EXPECTED={'LinuxFilesystemClassifierTest':4,'InspectorEnvironmentReaderTest':8,'InspectorEnvironmentPublisherTest':13,'InspectorEnvironmentFilesTest':10,'MaintenanceRunFilesTest':39,'DurableRecordFilesTest':12,'StartupPermitFilesTest':15}
MODULES=['protocol','storage','bootstrap','batch']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
os.umask(0o077);OUT.mkdir(mode=0o700);(OUT/'tmp').mkdir(mode=0o700)
assert __import__('shutil').disk_usage(BASE).free>=10*1024**3
assert not any((SOURCE/('src/schubert-nk-'+m)/'target').exists()for m in MODULES)
inputs={str(p.relative_to(SOURCE)):sha(p)for p in SOURCE.rglob('*')if p.is_file()}
env={**os.environ,'JAVA_HOME':str(BASE/'tools/jdk-25.0.4'),'PATH':str(BASE/'tools/jdk-25.0.4/bin')+':'+os.environ['PATH'],'MAVEN_OPTS':'-Xmx768m -Djava.io.tmpdir='+str(OUT/'tmp'),'SCHUBERT_PG_ROOT':str(BASE/'tools/postgresql18/usr'),'SCHUBERT_SHELLCHECK':str(BASE/'tools/shellcheck-0.11.0')};env.pop('JAVA_TOOL_OPTIONS',None)
args=[str(BASE/'tools/maven/bin/mvn'),'-o','--no-transfer-progress','-Dstyle.color=never','-Djansi.force=false','-Djava.io.tmpdir='+str(OUT/'tmp'),'-Dmaven.repo.local='+str(BASE/'m2/repository'),'-pl','src/schubert-nk-storage,src/schubert-nk-batch','-am','-Dtest='+','.join(EXPECTED),'-Dsurefire.failIfNoSpecifiedTests=false','spotless:check','test-compile','jar:test-jar','test','spotbugs:check','jacoco:report','jar:jar']
start=datetime.datetime.now(datetime.timezone.utc)
with(OUT/'begin.safe.json').open('x')as f:json.dump({'startUTC':start.isoformat(),'pid':os.getpid(),'ticks':int(Path('/proc/self/stat').read_text().rpartition(')')[2].split()[19]),'inputs':inputs,'sourceSnapshot':SOURCE_HEAD,'command':args,'expectedSuites':EXPECTED,'compileOnlyUnselectedModules':['protocol','bootstrap'],'formalAccepted':False},f,sort_keys=True);f.flush();os.fsync(f.fileno())
with(OUT/'maven.private.log').open('xb')as f:r=subprocess.run(args,cwd=SOURCE,env=env,stdout=f,stderr=subprocess.STDOUT,umask=0o027);f.flush();os.fsync(f.fileno())
results={};static={};coverage={}
for module in MODULES:
 target=SOURCE/('src/schubert-nk-'+module)/'target'
 for p in(target/'surefire-reports').glob('TEST-*.xml'):
  x=ET.parse(p).getroot();n=x.attrib['name'].split('.')[-1];assert n in EXPECTED and n not in results
  results[n]={**{k:int(x.attrib[k])for k in ['tests','failures','errors','skipped']},'module':module,'xmlSha256':sha(p),'freshAfterBegin':p.stat().st_mtime_ns>=int(start.timestamp()*1e9)}
 p=target/'spotbugsXml.xml';static[module]=len(ET.parse(p).getroot().findall('BugInstance'))if p.exists()else None
 p=target/'site/jacoco/jacoco.xml'
 if p.exists():
  for c in ET.parse(p).getroot().findall('.//class'):
   if c.attrib['name'].endswith('/LinuxFilesystemClassifier'):coverage[c.attrib['name']]={v.attrib['type']:{k:int(v.attrib[k])for k in ['missed','covered']}for v in c.findall('counter')}
end=datetime.datetime.now(datetime.timezone.utc)
passed=r.returncode==0 and set(results)==set(EXPECTED)and all(v['tests']==EXPECTED[n]and v['failures']==v['errors']==v['skipped']==0 and v['freshAfterBegin']for n,v in results.items())and all(v==0 for v in static.values())and all(sha(SOURCE/p)==h for p,h in inputs.items())
manifest={'run':'PG1525-selected-v1','actualExit':0 if passed else 1,'mavenExit':r.returncode,'sourceSnapshot':SOURCE_HEAD,'startUTC':start.isoformat(),'endUTC':end.isoformat(),'elapsedSeconds':(end-start).total_seconds(),'suites':results,'staticIssues':static,'classifierCoverage':coverage,'sourceInputsUnchanged':all(sha(SOURCE/p)==h for p,h in inputs.items()),'logSha256':sha(OUT/'maven.private.log'),'formalAccepted':False,'wholeRegressionNotRun':True,'compileOnlyUnselectedNotPtPass':True,'vmMutation0':True}
with(OUT/'manifest.safe.json').open('x')as f:json.dump(manifest,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps(manifest,sort_keys=True));raise SystemExit(manifest['actualExit'])
'''

def main():
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
 os.umask(0o077);out=W/'pg1525-server-selected-v1';out.mkdir(mode=0o700)
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();archive=out/'source.tar'
 with archive.open('xb')as f:subprocess.run(['git','archive',head,'src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT,stdout=f,check=True);f.flush();os.fsync(f.fileno())
 helper=out/'pg1525_server_selected.py';helper.write_text('SOURCE_HEAD='+repr(head)+'\n'+SERVER);compile(helper.read_text(),'<isolated selected filesystem PT>','exec')
 files=[(archive,REMOTE+'/transfer/PG1525-source.tar'),(helper,REMOTE+'/tools/pg1525_server_selected.py')]
 hashes={d:hashlib.sha256(p.read_bytes()).hexdigest()for p,d in files}
 code,status=run('test ! -e '+REMOTE+'/source-selected-PG1525 && test ! -e '+REMOTE+'/runs/PG1525-selected-v1 && '+' && '.join('test ! -e '+d for _,d in files));assert code==0
 for p,d in files:code,status=copy(str(p),d,timeout=300);assert code==0
 code,status=run('sha256sum '+' '.join(hashes));assert code==0 and all(x in status for x in hashes.values())
 with(out/'begin.safe.json').open('x')as f:json.dump({'sourceSnapshot':head,'transferHashes':hashes,'expectedTests':101,'expectedSuites':7,'trigger':'SSC269 production filesystem implementation and all delegated original/runtime IO selected suites','formalAccepted':False,'vmMutation0':True},f,sort_keys=True);f.flush();os.fsync(f.fileno())
 code,status=run('mkdir -m700 '+REMOTE+'/source-selected-PG1525 && tar -xf '+REMOTE+'/transfer/PG1525-source.tar -C '+REMOTE+'/source-selected-PG1525',timeout=120);assert code==0
 code,status=run('python3 -B '+REMOTE+'/tools/pg1525_server_selected.py',timeout=1200)
 (out/'observer.private.log').write_text(status)
 v={'run':'PG1525-server-selected-v1','actualExit':code,'sourceSnapshot':head,'formalAccepted':False,'qualificationPending':True,'vmMutation0':True}
 with(out/'manifest.safe.json').open('x')as f:json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 print(json.dumps(v));return code
if __name__=='__main__':raise SystemExit(main())
