"""New-source Web update assets: mandatory Node and HTTP consumer selected regression."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy, run
from pg1446_current_cold_stage import W

ROOT = Path(__file__).resolve().parents[2]
BASE = '/home/mini/schubert-nk-pgpt'
CLASSES = ['OperationPostScriptTest', 'UserAdminControllerTest', 'QuestionControllerTest',
           'NotificationControllerTest', 'WebAuthorizationFilterTest', 'UserBusinessControllerTest', 'TargetBusinessControllerTest']
SERVER = r'''
import datetime,hashlib,json,os,subprocess,tarfile,xml.etree.ElementTree as E
from pathlib import Path
os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG2646-v3';source=b/'source-web-PG2646-v3';transfer=b/'transfer/PG2646-v3'
def require(v):
 if not v:raise ValueError('new-source selected Web update contract refused')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out.mkdir(mode=0o700);source.mkdir(mode=0o700);archive=transfer/'source.tar';require(sha(archive)==INPUT['archiveSha256'])
with tarfile.open(archive)as t:t.extractall(source,filter='data')
inputs={str(p.relative_to(source)):sha(p)for p in source.rglob('*')if p.is_file()}
env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS')};env['JAVA_HOME']=str(b/'tools/jdk-25.0.4');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH'];env['SCHUBERT_PG_ROOT']=str(b/'tools/postgresql18/usr');env['SCHUBERT_SHELLCHECK']=str(b/'tools/shellcheck-0.11.0')
base=[str(b/'tools/maven/bin/mvn'),'-o','--no-transfer-progress','-Dstyle.color=never','-Djansi.force=false','-Dmaven.repo.local='+str(b/'m2/repository'),'-Dnk.pt.repository='+str(source),'-Dnk.pt.node='+str(b/'tools/node-v24.19.0/bin/node')]
deps=base+['-pl','src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api','clean','spotless:check','test-compile','jar:test-jar','jar:jar','install:install']
with(out/'dependency-compile.private.log').open('xb')as f:d=subprocess.run(deps,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
require(d.returncode==0)
args=base+['-pl','src/schubert-nk-web','-Dtest='+','.join(INPUT['classes']),'clean','spotless:check','test-compile','test','spotbugs:check','jacoco:report','jar:jar']
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
with(out/'maven.private.log').open('xb')as f:r=subprocess.run(args,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900)
require(r.returncode==0);module=source/'src/schubert-nk-web';xmls=list((module/'target/surefire-reports').glob('TEST-*.xml'));observed=set();count=0;hashes={}
for p in xmls:
 x=E.parse(p).getroot();name=x.get('name').rsplit('.',1)[-1];observed.add(name);cs=x.findall('testcase');require(len(cs)==int(x.get('tests'))and all(x.get(k)=='0'for k in('failures','errors','skipped')));require(not any(x.findall('.//'+k)for k in('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')));count+=len(cs);hashes[p.name]=sha(p)
require(observed==set(INPUT['classes'])and len(xmls)==len(INPUT['classes']))
script=module/'src/main/resources/static/js/operation-post-submit.js';tap=(module/'target/pt-operation-script/node.tap').read_text();require(all(x in tap.splitlines()for x in('# tests 6','# pass 6','# fail 0','# skipped 0','# todo 0','# cancelled 0'))and any('operation-post-submit.js' in x and '100.00 |   100.00 |  100.00' in x for x in tap.splitlines()))
issues=0
for p in source.glob('src/*/target/spotbugsXml.xml'):issues+=len(E.parse(p).getroot().findall('.//BugInstance'))
require(issues==0 and all(sha(source/n)==h for n,h in inputs.items()))
value={'actualExit':0,'candidateSource':INPUT['head'],'sourceSnapshot':INPUT['head'],'startUTC':started,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tests':count,'suites':len(xmls),'classes':sorted(observed),'xmlHashes':hashes,'scriptSha256':sha(script),'nodeTapSha256':sha(module/'target/pt-operation-script/node.tap'),'logSha256':sha(out/'maven.private.log'),'staticIssues':issues,'NodeCases':6,'NodeThreeCounters100':True,'FESFlakyNotRun':0,'vmActions':0,'nativeNotAccepted':True,'wholeRegressionNotAccepted':True,'formalAccepted':False,'input':INPUT}
(out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k not in('input','xmlHashes','classes')}))
'''


def main():
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean new-source Web candidate required')
    for name in CLASSES:
        if len(list((ROOT / 'src/schubert-nk-web/src/test/java').rglob(name + '.java'))) != 1:
            raise ValueError('all mandatory selected classes must exist')
    os.umask(0o077);out=W/'pg2646-operation-post-web-selected-v3';out.mkdir(mode=0o700)
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();archive=out/'source.tar'
    archive.write_bytes(subprocess.check_output(['git','archive','--format=tar',head,'pom.xml','mvnw','.mvn','src','program/characterization','documents/100_RD','documents/200_UI','documents/300_SS']))
    inputs={'head':head,'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'classes':CLASSES}
    code='INPUT='+repr(inputs)+'\n'+SERVER;compile(code,'<selected Web update whole namespace>','exec');script=out/'selected.private.py';script.write_text(code)
    c,_=run('test ! -e '+BASE+'/runs/PG2646-v3 && test ! -e '+BASE+'/source-web-PG2646-v3 && test ! -e '+BASE+'/transfer/PG2646-v3 && mkdir -m700 '+BASE+'/transfer/PG2646-v3',30)
    if c:raise ValueError('fresh new-source namespace required')
    for p in (archive,script):
        c,_=copy(p,BASE+'/transfer/PG2646-v3/',60)
        if c:raise ValueError('immutable candidate source transfer required')
    c,o=run('python3 -B '+BASE+'/transfer/PG2646-v3/selected.private.py',1300)
    (out/'server.private.log').write_text(o);value={'actualExit':c,'candidateSource':head,'payloadSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False}
    if not c:value['result']=json.loads(next(x for x in o.splitlines()if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return c


if __name__ == '__main__':
    raise SystemExit(main())
