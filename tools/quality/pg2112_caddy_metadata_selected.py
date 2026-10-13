"""Fresh isolated changed-Main batch PT on LAN. No VM or business mutation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy, run

ROOT = Path(__file__).resolve().parents[2]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
BASE = '/home/mini/schubert-nk-pgpt'
SERVER = r'''
import datetime,hashlib,json,os,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
os.umask(0o077)
b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG2112-selected-v1';source=b/'source-selected-PG2112'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(v):
 if not v:raise ValueError('isolated changed-Main Caddy PT qualification refused')
require(not out.exists() and not source.exists())
require(os.statvfs(b).f_bavail*os.statvfs(b).f_frsize>=10*1024**3)
archive=b/'transfer/PG2112-source.tar';require(sha(archive)==ARCHIVE_SHA)
out.mkdir(mode=0o700);source.mkdir(mode=0o700);(out/'tmp').mkdir(mode=0o700)
subprocess.run(['tar','-xf',str(archive),'-C',str(source)],check=True)
inputs={str(p.relative_to(source)):sha(p)for p in source.rglob('*')if p.is_file()}
modules=['protocol','storage','bootstrap','batch']
args=[str(b/'tools/maven/bin/mvn'),'-o','--no-transfer-progress','-Dstyle.color=never','-Djansi.force=false','-Dmaven.repo.local='+str(b/'m2/repository'),'-pl',','.join('src/schubert-nk-'+m for m in modules),'-am','-Dtest=CaddyPublicMetadataTest,CaddyPublicConfigurationTest,CaddyPublicCaMetadataTest,CaddyAddressBoundaryTest','-Dsurefire.failIfNoSpecifiedTests=false','-DfailIfNoTests=false','spotless:check','test-compile','jar:test-jar','test','spotbugs:check','jacoco:report','jar:jar']
env={k:v for k,v in os.environ.items()if k not in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS']}
env.update(JAVA_HOME=str(b/'tools/jdk-25.0.4'),PATH=str(b/'tools/jdk-25.0.4/bin')+':'+env['PATH'],MAVEN_OPTS='-Xmx768m -Djava.io.tmpdir='+str(out/'tmp'),SCHUBERT_PG_ROOT=str(b/'tools/postgresql18/usr'))
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with(out/'begin.safe.json').open('x')as f:json.dump({'sourceSnapshot':HEAD,'archiveSha256':ARCHIVE_SHA,'command':args,'startedUTC':start,'pid':os.getpid(),'formalAccepted':False,'vmActions0':True},f)
with(out/'maven.private.log').open('xb')as f:r=subprocess.run(args,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT)
counts={};issues={};coverage={}
for m in modules:
 t=source/'src'/('schubert-nk-'+m)/'target'
 for p in (t/'surefire-reports').glob('TEST-*.xml'):
  x=ET.parse(p).getroot();counts[x.attrib['name']]={k:int(x.attrib[k])for k in ['tests','failures','errors','skipped']}
 p=t/'spotbugsXml.xml'
 issues[m]=len(ET.parse(p).getroot().findall('BugInstance'))if p.exists()else None
 p=t/'site/jacoco/jacoco.xml'
 if p.exists():
  x=ET.parse(p).getroot()
  for c in x.findall('.//class'):
   if c.attrib['name']=='dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration':coverage={q.attrib['type']:{k:int(q.attrib[k])for k in ['missed','covered']}for q in c.findall('counter')}
same=all(sha(source/p)==h for p,h in inputs.items())
result={'actualExit':r.returncode,'sourceSnapshot':HEAD,'archiveSha256':ARCHIVE_SHA,'sourceInputsStable':same,'tests':counts,'staticIssues':issues,'classCounters':coverage,'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'logSha256':sha(out/'maven.private.log'),'formalAccepted':False,'wholeRegressionNotRun':True,'nativeNotRun':True,'vmActions0':True,'inputs':inputs}
with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
require(r.returncode==0 and same and set(counts)=={'dev.codex.schubert.nk.batch.file.'+n for n in ['CaddyPublicMetadataTest','CaddyPublicConfigurationTest','CaddyPublicCaMetadataTest','CaddyAddressBoundaryTest']})
require(counts['dev.codex.schubert.nk.batch.file.CaddyPublicMetadataTest']=={'tests':4,'failures':0,'errors':0,'skipped':0})
require(all(v[k]==0 for v in counts.values()for k in ['failures','errors','skipped'])and all(v==0 for v in issues.values()))
print(json.dumps({'actualExit':0,'tests':counts,'staticIssues':issues,'classCounters':coverage,'sourceSnapshot':HEAD,'sourceInputsStable':same,'manifestSha256':sha(out/'manifest.safe.json'),'formalAccepted':False}))
'''

def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):
        raise ValueError('fixed clean source required')
    os.umask(0o077)
    out=W/'pg2112-caddy-metadata-selected-v1';out.mkdir(mode=0o700)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    archive=out/'source.tar'
    with archive.open('xb')as f:
        subprocess.run(['git','archive',head,'src','pom.xml','mvnw','.mvn','program/characterization'],cwd=ROOT,stdout=f,check=True)
    code='HEAD='+repr(head)+'\nARCHIVE_SHA='+repr(hashlib.sha256(archive.read_bytes()).hexdigest())+'\n'+SERVER
    compile(code,'<actual changed-Main Caddy selected PT>','exec')
    script=out/'server.private.py';script.write_text(code)
    for p,dest in [(archive,BASE+'/transfer/PG2112-source.tar'),(script,BASE+'/tools/pg2112-caddy-selected.py')]:
        status,output=run('test ! -e '+dest,timeout=30)
        if status:raise ValueError('new-only transport slot required')
        status,output=copy(str(p),dest,timeout=120)
        if status:raise ValueError('qualified archive transfer required')
    status,output=run('python3 -B '+BASE+'/tools/pg2112-caddy-selected.py',timeout=1800)
    (out/'observer.private.log').write_text(output)
    result={'actualExit':status,'sourceSnapshot':head,'payloadSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False,'vmActions0':True}
    if not status:result.update(json.loads(next(l for l in output.splitlines()if l.startswith('{'))))
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True))
    print(json.dumps(result));return status

if __name__=='__main__':raise SystemExit(main())
