"""BUG1245 deterministic vendor queue scheduling reproduction; no PT credit."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy,run
from pg1446_current_cold_stage import W

ROOT=Path(__file__).resolve().parents[2]
BASE='/home/mini/schubert-nk-pgpt'
SERVER=r"""
import datetime,hashlib,json,os,subprocess,tarfile,xml.etree.ElementTree as E
from pathlib import Path
os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG2690-before-v1';source=b/'source-expiry-PG2690-before-v1';transfer=b/'transfer/PG2690-before-v1'
def require(v):
 if not v:raise ValueError('one deterministic expiry fixture contract required')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out.mkdir(mode=0o700);source.mkdir(mode=0o700);archive=transfer/'source.tar';require(sha(archive)==INPUT['archiveSha256'])
with tarfile.open(archive)as t:t.extractall(source,filter='data')
inputs={str(p.relative_to(source)):sha(p)for p in source.rglob('*')if p.is_file()}
test=source/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/ArtemisExpiryPurgeClientTest.java';raw=test.read_text()
old='''      var requestQueue =
          broker.getActiveMQServer().locateQueue(SimpleString.of("nk.sync.request.q"));'''
require(raw.count(old)==1);raw=raw.replace(old,'')
marker='      var message = web.createMessage(true);'
barrier='''      var requestQueue = broker.getActiveMQServer().locateQueue(SimpleString.of("nk.sync.request.q"));
      var entered = new java.util.concurrent.CountDownLatch(1);
      var release = new java.util.concurrent.CountDownLatch(1);
      requestQueue.getExecutor().execute(() -> {
        entered.countDown();
        try {
          if (!release.await(5, java.util.concurrent.TimeUnit.SECONDS)) throw new AssertionError("fixture gate deadline");
        } catch (InterruptedException interrupted) {
          Thread.currentThread().interrupt();throw new AssertionError("fixture gate interrupted");
        }
      });
      assertTrue(entered.await(5, java.util.concurrent.TimeUnit.SECONDS));
      try {
'''
require(raw.count(marker)==1);raw=raw.replace(marker,barrier+marker)
marker='      long expiryCount ='
require(raw.count(marker)==1);raw=raw.replace(marker,'      } finally { release.countDown(); }\n'+marker)
test.write_text(raw);modified=sha(test)
env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS')};env['JAVA_HOME']=str(b/'tools/jdk-25.0.4');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH'];env['SCHUBERT_PG_ROOT']=str(b/'tools/postgresql18/usr');env['SCHUBERT_SHELLCHECK']=str(b/'tools/shellcheck-0.11.0')
base=[str(b/'tools/maven/bin/mvn'),'-o','--no-transfer-progress','-Dstyle.color=never','-Djansi.force=false','-Dmaven.repo.local='+str(b/'m2/repository'),'-Dnk.pt.repository='+str(source),'-Djacoco.skip=true']
deps=base+['-pl','src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap','test-compile','jar:test-jar','jar:jar','install:install']
with(out/'dependency.private.log').open('xb')as f:d=subprocess.run(deps,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
require(d.returncode==0)
args=base+['-pl','src/schubert-nk-batch','-Dtest=ArtemisExpiryPurgeClientTest#opsMq026RealBrokerRemovesOnlyActualExpiredMessage','test-compile','test']
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with(out/'maven.private.log').open('xb')as f:r=subprocess.run(args,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
xml=source/'src/schubert-nk-batch/target/surefire-reports/TEST-dev.codex.schubert.nk.batch.mq.ArtemisExpiryPurgeClientTest.xml';x=E.parse(xml).getroot();cases=x.findall('testcase');require(r.returncode!=0 and len(cases)==1 and x.get('failures')=='1'and x.get('errors')==x.get('skipped')=='0')
failure=cases[0].find('failure');require(failure is not None and failure.get('type')=='org.opentest4j.AssertionFailedError'and failure.get('message')=='expected: <1> but was: <0>')
require(all(sha(source/p)==h for p,h in inputs.items()if p!=str(test.relative_to(source))))
v={'actualExit':0,'diagnosticMavenExit':r.returncode,'diagnosticModifiedFixtureSha256':modified,'beforeFixtureSha256':inputs[str(test.relative_to(source))],'sourceSnapshot':INPUT['head'],'productionSource':INPUT['productionSource'],'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'expectedOriginalAssertionFailure':True,'failureType':failure.get('type'),'testId':'PT-OPS-MQ-026','xmlSha256':sha(xml),'logSha256':sha(out/'maven.private.log'),'sameMainUnchanged':True,'coverageCredit':0,'productionPtCredit':0,'vmActions':0,'formalAccepted':False}
(out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v))
"""


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean frozen diagnostic operator required')
    os.umask(0o077);out=W/'pg2690-expiry-before-v1';out.mkdir(mode=0o700)
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();archive=out/'source.tar'
    archive.write_bytes(subprocess.check_output(['git','archive','--format=tar',head,'pom.xml','mvnw','.mvn','src','program/characterization','documents/100_RD','documents/200_UI','documents/300_SS']))
    inputs={'head':head,'productionSource':'04207efc3ad78bca75942153a90c70985064c988','archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
    code='INPUT='+repr(inputs)+'\n'+SERVER;compile(code,'<deterministic expiry vendor diagnostic>','exec');script=out/'diagnostic.private.py';script.write_text(code)
    c,_=run('test ! -e '+BASE+'/runs/PG2690-before-v1 && test ! -e '+BASE+'/source-expiry-PG2690-before-v1 && test ! -e '+BASE+'/transfer/PG2690-before-v1 && mkdir -m700 '+BASE+'/transfer/PG2690-before-v1',30)
    if c:raise ValueError('fresh diagnostic namespace required')
    for p in (archive,script):
        c,_=copy(p,BASE+'/transfer/PG2690-before-v1/',60)
        if c:raise ValueError('immutable diagnostic transfer required')
    c,o=run('python3 -B '+BASE+'/transfer/PG2690-before-v1/diagnostic.private.py',700)
    (out/'server.private.log').write_text(o);v={'actualExit':c,'payloadSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False}
    if not c:v['result']=json.loads(next(x for x in o.splitlines()if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return c


if __name__=='__main__':raise SystemExit(main())
