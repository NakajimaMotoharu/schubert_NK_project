"""One current Protocol regression for independent header/18 enum oracles; Main unchanged."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy, run
from pg1446_current_cold_stage import W
from pg2600_retention_group_full_six import SOURCE

ROOT = Path(__file__).resolve().parents[2]
BASE = '/home/mini/schubert-nk-pgpt'
SLOT = 'pg2634-protocol-oracle-regression-v2'
SERVER = r'''
import datetime,hashlib,json,os,subprocess,tarfile,xml.etree.ElementTree as ET,zipfile
from pathlib import Path
os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG2634-v2';source=b/'source-protocol-PG2634-v2';transfer=b/'transfer/PG2634-v2'
def require(v):
 if not v:raise ValueError('exact current Protocol oracle regression refused')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out.mkdir(mode=0o700);source.mkdir(mode=0o700);archive=transfer/'source.tar';require(sha(archive)==INPUT['archiveSha256'])
with tarfile.open(archive)as t:t.extractall(source,filter='data')
module=source/'src/schubert-nk-protocol';inputs={str(p.relative_to(source)):sha(p)for p in source.rglob('*')if p.is_file()}
env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS')};env['JAVA_HOME']=str(b/'tools/jdk-25.0.4');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
args=[str(b/'tools/maven/bin/mvn'),'-o','--no-transfer-progress','-Dstyle.color=never','-Djansi.force=false','-Dmaven.repo.local='+str(b/'m2/repository'),'-Dnk.pt.repository='+str(source),'-pl','src/schubert-nk-protocol','clean','spotless:check','test-compile','test','spotbugs:check','jacoco:report','jar:jar']
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
with(out/'maven.private.log').open('xb')as f:r=subprocess.run(args,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240)
require(r.returncode==0);xmls=list((module/'target/surefire-reports').glob('TEST-*.xml'));require(len(xmls)==17);tests=0
for p in xmls:
 x=ET.parse(p).getroot();require(all(x.get(k)=='0'for k in('failures','errors','skipped')));require(not x.findall('.//failure')and not x.findall('.//error')and not x.findall('.//skipped'));tests+=int(x.get('tests'))
require(tests==82)
coverage=ET.parse(module/'target/site/jacoco/jacoco.xml').getroot();counters={x.get('type'):{'missed':int(x.get('missed')),'covered':int(x.get('covered'))}for x in coverage.findall('counter')}
require(all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in('LINE','METHOD','CLASS','BRANCH')))
spots=module/'target/spotbugsXml.xml';require(spots.is_file()and not ET.parse(spots).getroot().findall('.//BugInstance'))
jar=module/'target/schubert-nk-protocol-0.1.0-SNAPSHOT.jar';old=b/'source-full-PG2620/src/schubert-nk-protocol/target/schubert-nk-protocol-0.1.0-SNAPSHOT.jar';require(sha(old)==INPUT['priorJarSha256'])
images=[]
for p in(old,jar):
 with zipfile.ZipFile(p)as z:
  require(len(z.namelist())==len(set(z.namelist())));images.append({n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()})
require(images[0]==images[1]);main=sum(n.endswith('.class')for n in images[1]);require(main==174)
require(all(sha(source/n)==h for n,h in inputs.items()))
value={'actualExit':0,'mavenExit':r.returncode,'source':INPUT['source'],'testSource':INPUT['head'],'startUTC':started,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tests':tests,'suites':len(xmls),'mainClasses':main,'coverage':counters,'staticIssues':0,'FESFlakyNotRun':0,'allProtocolMainAndResourcesSameBytes':True,'input':INPUT,'command':args,'xmlHashes':{p.name:sha(p)for p in xmls},'jarSha256':sha(jar),'coverageXmlSha256':sha(module/'target/site/jacoco/jacoco.xml'),'staticSha256':sha(spots),'logSha256':sha(out/'maven.private.log'),'vmActions':0,'formalAccepted':False,'fullSixIntegrationPending':True}
(out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k not in('input','command','xmlHashes','coverage')}))
'''


def main():
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('fixed clean Test source required')
    if subprocess.check_output(['git', 'diff', SOURCE, 'HEAD', '--', 'src/schubert-nk-protocol/src/main', 'src/schubert-nk-protocol/pom.xml', 'pom.xml']):
        raise ValueError('qualified Production Protocol unchanged required')
    full = json.loads((W / 'pg2621-permit-expiry-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if full['actualExit'] != 0 or full['result']['productionSource'] != SOURCE:
        raise ValueError('actual current Main full required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    archive=out/'source.tar';archive.write_bytes(subprocess.check_output(['git','archive','--format=tar',head,'pom.xml','mvnw','.mvn','src','program/characterization','documents/100_RD','documents/200_UI','documents/300_SS']))
    inputs={'source':SOURCE,'head':head,'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'priorJarSha256':full['result']['jarHashes']['protocol']}
    code='INPUT='+repr(inputs)+'\n'+SERVER;compile(code,'<current Protocol independent oracle regression>','exec')
    script=out/'regression.private.py';script.write_text(code)
    c,_=run('test ! -e '+BASE+'/runs/PG2634-v2 && test ! -e '+BASE+'/source-protocol-PG2634-v2 && test ! -e '+BASE+'/transfer/PG2634-v2 && mkdir -m700 '+BASE+'/transfer/PG2634-v2',30)
    if c:raise ValueError('fresh Protocol regression namespace required')
    for p in(archive,script):
        c,_=copy(p,BASE+'/transfer/PG2634-v2/',60)
        if c:raise ValueError('immutable Protocol input transfer required')
    c,o=run('python3 -B '+BASE+'/transfer/PG2634-v2/regression.private.py',300)
    (out/'server.private.log').write_text(o)
    value={'actualExit':c,'source':SOURCE,'testSource':head,'payloadSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False}
    if not c:value['result']=json.loads(next(x for x in o.splitlines()if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return c


if __name__=='__main__':
    raise SystemExit(main())
