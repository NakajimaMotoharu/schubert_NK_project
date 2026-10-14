"""BUG1245/YKT1011 bounded real queue recurrence plus RBAC and unknown contract."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy,run
from pg1446_current_cold_stage import W

ROOT=Path(__file__).resolve().parents[2];BASE='/home/mini/schubert-nk-pgpt'
CLASSES={'ArtemisExpiryPurgeClientTest':6,'ArtemisExpiryManagementAuthorizationTest':1,'ArtemisUnknownBoundaryTest':4}
SERVER=r'''
import datetime,hashlib,json,os,subprocess,tarfile,xml.etree.ElementTree as E
from pathlib import Path
os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG2692-selected-v1';source=b/'source-expiry-PG2692-selected-v1';transfer=b/'transfer/PG2692-selected-v1'
def require(v):
 if not v:raise ValueError('complete selected expiry fixture qualification required')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out.mkdir(mode=0o700);source.mkdir(mode=0o700);archive=transfer/'source.tar';require(sha(archive)==INPUT['archiveSha256'])
with tarfile.open(archive)as t:t.extractall(source,filter='data')
inputs={str(p.relative_to(source)):sha(p)for p in source.rglob('*')if p.is_file()}
env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS')};env['JAVA_HOME']=str(b/'tools/jdk-25.0.4');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH'];env['SCHUBERT_PG_ROOT']=str(b/'tools/postgresql18/usr');env['SCHUBERT_SHELLCHECK']=str(b/'tools/shellcheck-0.11.0')
base=[str(b/'tools/maven/bin/mvn'),'-o','--no-transfer-progress','-Dstyle.color=never','-Djansi.force=false','-Dmaven.repo.local='+str(b/'m2/repository'),'-Dnk.pt.repository='+str(source)]
deps=base+['-pl','src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap','spotless:check','test-compile','jar:test-jar','jar:jar','install:install']
with(out/'dependency.private.log').open('xb')as f:d=subprocess.run(deps,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
require(d.returncode==0)
args=base+['-pl','src/schubert-nk-batch','-Dtest='+','.join(INPUT['classes']),'spotless:check','test-compile','test','spotbugs:check','jacoco:report','jar:jar']
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with(out/'maven.private.log').open('xb')as f:r=subprocess.run(args,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
require(r.returncode==0);module=source/'src/schubert-nk-batch';xmls=list((module/'target/surefire-reports').glob('TEST-*.xml'));observed={};hashes={};cases=[]
for p in xmls:
 x=E.parse(p).getroot();name=x.get('name').rsplit('.',1)[-1];require(name not in observed);cs=x.findall('testcase');require(len(cs)==int(x.get('tests'))and all(x.get(k)=='0'for k in('failures','errors','skipped')));require(not any(x.findall('.//'+k)for k in('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')));observed[name]=len(cs);hashes[p.name]=sha(p);cases.extend((x.get('name'),c.get('name'))for c in cs)
require(observed==INPUT['classes']and len(set(cases))==len(cases))
issues=len(E.parse(module/'target/spotbugsXml.xml').getroot().findall('.//BugInstance'));require(issues==0 and all(sha(source/n)==h for n,h in inputs.items()))
report=E.parse(module/'target/site/jacoco/jacoco.xml').getroot();c=next(x for x in report.iter('class')if x.get('name')=='dev/codex/schubert/nk/batch/mq/ArtemisExpiryPurgeClient');counters={x.get('type'):{'missed':int(x.get('missed')),'covered':int(x.get('covered'))}for x in c.findall('counter')}
for name in ['LINE','METHOD','CLASS','BRANCH']:require(counters[name]['missed']==0 and counters[name]['covered']>0)
v={'actualExit':0,'sourceSnapshot':INPUT['head'],'productionSource':INPUT['productionSource'],'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tests':len(cases),'suites':len(xmls),'observed':observed,'xmlHashes':hashes,'cases':cases,'logSha256':sha(out/'maven.private.log'),'staticIssues':issues,'expiryClassCounters':counters,'inputUnchanged':True,'vmActions':0,'formalAccepted':False,'wholeRegressionAccepted':False}
(out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps({k:x for k,x in v.items()if k not in('cases','xmlHashes')}))
'''


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed selected operator required')
    os.umask(0o077);out=W/'pg2692-expiry-selected-v1';out.mkdir(mode=0o700)
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();archive=out/'source.tar'
    archive.write_bytes(subprocess.check_output(['git','archive','--format=tar',head,'pom.xml','mvnw','.mvn','src','program/characterization','documents/100_RD','documents/200_UI','documents/300_SS']))
    inputs={'head':head,'productionSource':'04207efc3ad78bca75942153a90c70985064c988','archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'classes':CLASSES}
    code='INPUT='+repr(inputs)+'\n'+SERVER;compile(code,'<complete expiry selected run>','exec');script=out/'selected.private.py';script.write_text(code)
    c,_=run('test ! -e '+BASE+'/runs/PG2692-selected-v1 && test ! -e '+BASE+'/source-expiry-PG2692-selected-v1 && test ! -e '+BASE+'/transfer/PG2692-selected-v1 && mkdir -m700 '+BASE+'/transfer/PG2692-selected-v1',30)
    if c:raise ValueError('fresh selected namespace required')
    for p in (archive,script):
        c,_=copy(p,BASE+'/transfer/PG2692-selected-v1/',60)
        if c:raise ValueError('immutable selected transfer required')
    c,o=run('python3 -B '+BASE+'/transfer/PG2692-selected-v1/selected.private.py',1200)
    (out/'server.private.log').write_text(o);v={'actualExit':c,'payloadSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False}
    if not c:v['result']=json.loads(next(x for x in o.splitlines()if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return c


if __name__=='__main__':raise SystemExit(main())
