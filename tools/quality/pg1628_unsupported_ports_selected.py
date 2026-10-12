"""Eight independent fail-closed contracts against frozen qualified Main bytes.

Only new test/helper classes and output are written. Existing test fixtures are
hashed before and after use; no production compilation, VM or business action.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy, run
from pg1609_current_ordinary_owned_stop_sources import SOURCE

ROOT = Path(__file__).resolve().parents[2]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
SLOT = 'pg1628-unsupported-ports-selected-v1'
BASE = '/home/mini/schubert-nk-pgpt'
FILES = [
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootRecoveryNativeAuthorityTest.java',
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/UnsupportedOriginalProofTest.java',
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/UnsupportedRootIdentityTest.java',
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/TransferCleanupFailureTest.java',
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/UnsupportedBackupVerificationTest.java',
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/UnsupportedServiceMarkerTest.java',
    'tools/quality/vm/050_s1/Pg1628SelectedLauncher.java',
    'tools/quality/vm/050_s1/NativeCoverage.java',
    'tools/quality/vm/050_s1/NativeCoverageXml471.java',
]
LIBRARIES = [
    'org/junit/jupiter/junit-jupiter-api/5.13.4/junit-jupiter-api-5.13.4.jar',
    'org/junit/jupiter/junit-jupiter-engine/5.13.4/junit-jupiter-engine-5.13.4.jar',
    'org/junit/platform/junit-platform-commons/1.13.4/junit-platform-commons-1.13.4.jar',
    'org/junit/platform/junit-platform-engine/1.13.4/junit-platform-engine-1.13.4.jar',
    'org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar',
    'org/apiguardian/apiguardian-api/1.1.2/apiguardian-api-1.1.2.jar',
    'org/opentest4j/opentest4j/1.3.0/opentest4j-1.3.0.jar',
    'org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar',
    'com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar',
    'org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar',
]

SERVER = r'''
import datetime,hashlib,json,os,shutil,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
os.umask(0o077)
b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG1628-selected-v1';transfer=b/'transfer/PG1628-selected-v1';source=b/'source-full-PG1532';repo=b/'m2/repository'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(v):
 if not v:raise ValueError('isolated unsupported port selection refused')
require(not out.exists() and shutil.disk_usage(b).free>=10*1024**3);out.mkdir(mode=0o700)
require(sha(b/'runs/PG1624-native-campaign-v1/manifest.safe.json')==INPUT['campaignManifestSha256'])
inp=json.loads((b/'runs/PG1618-native-v1/input.safe.json').read_bytes());full=inp['qualifiedFull'];require(inp['productionSource']==INPUT['productionSource'])
require(sha(b/'runs/PG1532-six-v1/manifest.safe.json')==full['serverManifestSha256'])
libraries=[]
for name,h in INPUT['libraries'].items():
 p=repo/name;require(sha(p)==h);libraries.append(str(p))
jars=[];hosts=[]
for m in ['protocol','storage','bootstrap','api','web','batch']:
 t=source/'src'/('schubert-nk-'+m)/'target';jar=t/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar');e=t/'jacoco.exec'
 require(sha(jar)==full['jarHashes'][m] and sha(e)==full['qualificationInputs'][m]['exec']);jars.append(str(jar));hosts.append(str(e))
fixtures=source/'src/schubert-nk-batch/target/test-classes'
fixture_hashes={str(p.relative_to(fixtures)):sha(p) for p in fixtures.rglob('*.class')}
require(fixture_hashes and 'dev/codex/schubert/nk/batch/file/BackupDatabaseWorkerTest$Fixture.class' in fixture_hashes)
for name,h in INPUT['files'].items():require(sha(transfer/name)==h)
classes=out/'classes';classes.mkdir(mode=0o700);(out/'tmp').mkdir(mode=0o700)
cp=':'.join(jars+[str(fixtures)]+libraries);jdk=b/'tools/jdk-25.0.4/bin'
started=datetime.datetime.now(datetime.timezone.utc)
commands=[]
def execute(label,args,timeout=45):
 commands.append(args)
 r=subprocess.run(args,capture_output=True,timeout=timeout,env={k:v for k,v in os.environ.items() if k not in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS']})
 (out/(label+'.private.log')).write_bytes(r.stdout+r.stderr)
 require(r.returncode==0)
 return r
compile_result=execute('compile',[str(jdk/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*[str(transfer/n) for n in INPUT['files']]])
require(not compile_result.stderr)
exec_path=out/'selected.exec';xml=out/'tests.xml';agent=repo/'org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
execution=execute('tests',[str(jdk/'java'),'--enable-native-access=ALL-UNNAMED','-Dfile.encoding=UTF-8','-Djava.io.tmpdir='+str(out/'tmp'),'-javaagent:'+str(agent)+'=destfile='+str(exec_path)+',append=false','-cp',str(classes)+':'+cp,'Pg1628SelectedLauncher',str(xml)],timeout=60)
require(b'PG1628 tests8 failures0 errors0 skipped0 aborted0 notRun0' in execution.stdout)
x=ET.parse(xml).getroot();require(x.attrib['tests']=='8' and all(x.attrib[k]=='0' for k in ['failures','errors','skipped']) and len(x.findall('testcase'))==8)
require(all(sha(fixtures/n)==h for n,h in fixture_hashes.items()))
streams=hosts+[str(b/'runs'/cohort/(str(i)+'.exec')) for cohort in ['PG1590-native-v1','PG1618-native-v1'] for i in range(8)]+[str(exec_path)]
coverage={};xml_hashes={}
for m,jar in zip(['protocol','storage','bootstrap','api','web','batch'],jars):
 r=execute(m+'-coverage',[str(jdk/'java'),'-cp',str(classes)+':'+cp,'NativeCoverage',jar,*streams]);coverage[m]=json.loads(r.stdout);require(coverage[m]['classByteMismatch']==0)
 p=out/(m+'.xml');r=execute(m+'-xml',[str(jdk/'java'),'-cp',str(classes)+':'+cp,'NativeCoverageXml471',jar,str(p),*streams]);require(b'classMismatch0=true' in r.stdout);xml_hashes[m]=sha(p)
require(all(sha(transfer/n)==h for n,h in INPUT['files'].items()))
result={'actualExit':0,'tests':8,'failures':0,'errors':0,'skipped':0,'aborted':0,'notRun':0,'productionSource':INPUT['productionSource'],'testSource':INPUT['testSource'],'testFiles':INPUT['files'],'libraries':INPUT['libraries'],'mainJarHashes':full['jarHashes'],'fixtureClassHashes':fixture_hashes,'fixtureBytesUnchanged':True,'javacWarnings':0,'classByteMismatch':0,'commands':commands,'startUTC':started.isoformat(),'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'xmlSha256':sha(xml),'execSha256':sha(exec_path),'coverage':coverage,'coverageXmlHashes':xml_hashes,'injectedPortsNotNativeOwnerProof':True,'wholeRegressionNotRun':True,'formalAccepted':False,'vmMutation0':True}
with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':0,'tests':result['tests'],'FESAbortedNotRun':0,'manifestSha256':sha(out/'manifest.safe.json'),'remaining':{k:sum(v[k]['missed']for v in coverage.values())for k in ['LINE','METHOD','CLASS','BRANCH']},'classByteMismatch':0,'javacWarnings':0,'formalAccepted':False,'vmMutation0':True}))
'''

def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):
        raise ValueError('fixed clean test/tool source required')
    changed = subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'],cwd=ROOT,text=True).splitlines()
    if any('/src/main/' in name or name.endswith('pom.xml') for name in changed):
        raise ValueError('qualified unchanged Production required')
    os.umask(0o077)
    out=W/SLOT;out.mkdir(mode=0o700)
    inp=json.loads((W/'pg1618-current-ordinary-native-qualified-v3/input.safe.json').read_bytes())
    libs=dict(inp['libraries']);repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    for name in LIBRARIES:libs[name]=hashlib.sha256((repo/name).read_bytes()).hexdigest()
    data={'productionSource':SOURCE,'testSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'files':{Path(p).name:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES},'libraries':libs,'campaignManifestSha256':json.loads((W/'pg1624-same-source-native-campaign-v1/manifest.safe.json').read_bytes())['manifestSha256']}
    code='INPUT='+repr(data)+'\n'+SERVER
    from pyflakes.api import check
    if check(code,'<actual isolated selected unsupported contracts>'):raise ValueError('generated static gate refused')
    script=out/'pg1628-selected.private.py';script.write_text(code)
    exit_code,output=run('test ! -e '+BASE+'/runs/PG1628-selected-v1 && test ! -e '+BASE+'/transfer/PG1628-selected-v1 && mkdir -m700 '+BASE+'/transfer/PG1628-selected-v1',timeout=30)
    if exit_code:raise ValueError('new-only selected namespace required')
    for p in [*(ROOT/n for n in FILES),script]:
        exit_code,output=copy(p,BASE+'/transfer/PG1628-selected-v1/',timeout=60)
        if exit_code:raise ValueError('fixed selected source transfer refused')
    exit_code,output=run('python3 -B '+BASE+'/transfer/PG1628-selected-v1/pg1628-selected.private.py',timeout=180)
    (out/'server.private.log').write_text(output)
    safe={'actualExit':exit_code,'scriptSha256':hashlib.sha256(code.encode()).hexdigest(),'testSource':data['testSource'],'productionSource':SOURCE,'formalAccepted':False}
    if exit_code==0:safe.update(json.loads(next(v for v in output.splitlines()if v.startswith('{'))))
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return exit_code

if __name__=='__main__':raise SystemExit(main())
