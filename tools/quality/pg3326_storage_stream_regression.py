"""Actual before/after Storage regression for BUG1289; immutable inputs, no VM action."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess

from lan_server import copy, run

ROOT = Path(__file__).resolve().parents[2]
W = ROOT.parent / 'pgpt-runs/PG379'
BASE = '/home/mini/schubert-nk-pgpt'
SOURCE = 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
TEST = 'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/StorageRootInspectionTest.java'
METHOD = 'a07AcceptsSixExistingRootsAndRejectsUnsafeExistingRoots'


def require(value, message):
    if not value:
        raise ValueError(message)


def classify(suites, before):
    cases = []
    failures = []
    for suite in suites:
        actual = suite.findall('testcase')
        require(len(actual) == int(suite.get('tests')), 'all actual cases required')
        require(not any('rerun' in n.tag.lower() or 'flaky' in n.tag.lower() for n in suite.iter()), 'no rerun/flaky')
        require(suite.get('errors') == suite.get('skipped') == '0', 'no error/skip')
        for case in actual:
            require(not case.findall('error') and not case.findall('skipped'), 'no case error/skip')
            identity = (case.get('classname'), case.get('name'))
            cases.append(identity)
            for failure in case.findall('failure'):
                failures.append((identity, failure.get('type'), failure.get('message', '')))
        require(int(suite.get('failures')) == sum(len(c.findall('failure')) for c in actual), 'failure summary matches cases')
    require(len(cases) == len(set(cases)), 'unique actual case identities')
    if before:
        require(len(suites) == 1 and len(cases) == 3 and len(failures) == 1, 'one genuine before failure among three actual tests required')
        identity, kind, message = failures[0]
        require(identity == ('dev.codex.schubert.nk.storage.StorageRootInspectionTest', METHOD)
                and kind == 'org.opentest4j.AssertionFailedError'
                and 'expected: <0> but was: <2>' in message, 'exact independent directory FD leak required')
    else:
        require(len(suites) == 23 and len(cases) == 163 and not failures, 'all actual Storage163/23 success required')
    return {'tests': len(cases), 'suites': len(suites), 'failures': len(failures), 'errors': 0, 'skipped': 0}


SERVER = r'''
import datetime,hashlib,json,os,subprocess,tarfile,xml.etree.ElementTree as ET,zipfile
from pathlib import Path
os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');slot=INPUT['slot'];out=b/'runs'/slot;source=b/('source-'+slot);transfer=b/'transfer'/slot
require(not out.exists()and not source.exists(),'new-only execution required')
require(__import__('shutil').disk_usage(b).free>10*1024**3,'preservation capacity required')
out.mkdir(mode=0o700);source.mkdir(mode=0o700)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
archive=transfer/'source.tar';require(sha(archive)==INPUT['archiveSha256'],'fixed archive required')
with tarfile.open(archive)as t:t.extractall(source,filter='data')
inputs={str(p.relative_to(source)):sha(p)for p in source.rglob('*')if p.is_file()}
module=source/'src/schubert-nk-storage';env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS')};env['JAVA_HOME']=str(b/'tools/jdk-25.0.4');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
args=[str(b/'tools/maven/bin/mvn'),'-o','--no-transfer-progress','-Dstyle.color=never','-Djansi.force=false','-Dmaven.repo.local='+str(b/'m2/repository'),'-Dnk.pt.repository='+str(source),'-pl','src/schubert-nk-storage','clean','spotless:check','test-compile','test']
if INPUT['before']:args.insert(1,'-Dtest=StorageRootInspectionTest')
else:args+=['spotbugs:check','jacoco:report','jar:jar']
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
with(out/'maven.private.log').open('xb')as f:r=subprocess.run(args,cwd=source,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300,umask=0o027)
xmls=sorted((module/'target/surefire-reports').glob('TEST-*.xml'));counts=classify([ET.parse(p).getroot()for p in xmls],INPUT['before'])
require(r.returncode==(1 if INPUT['before']else 0),'genuine Maven exit required')
value={'actualExit':0,'mavenExit':r.returncode,'counts':counts,'source':INPUT['source'],'testSource':INPUT['head'],'startUTC':started,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'testSha256':sha(source/INPUT['testPath']),'xmlHashes':{p.name:sha(p)for p in xmls},'command':args,'logSha256':sha(out/'maven.private.log'),'before':INPUT['before'],'childUmask':'0027','privateObserverUmask':'0077','vmActions':0,'newPtCredit':0,'formalUpdated':False,'fullSixIntegrationPending':True}
if not INPUT['before']:
 cxml=module/'target/site/jacoco/jacoco.xml';coverage=ET.parse(cxml).getroot();counters={x.get('type'):{'missed':int(x.get('missed')),'covered':int(x.get('covered'))}for x in coverage.findall('counter')};require(all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in('LINE','METHOD','CLASS','BRANCH')),'Storage four100 required')
 spots=module/'target/spotbugsXml.xml';require(not ET.parse(spots).getroot().findall('.//BugInstance'),'static0 required')
 old=b/'source-full-PG3302/src/schubert-nk-storage/target/schubert-nk-storage-0.1.0-SNAPSHOT.jar';jar=module/'target/schubert-nk-storage-0.1.0-SNAPSHOT.jar';require(sha(old)==INPUT['priorJarSha256'],'qualified original Jar required');images=[]
 for p in(old,jar):
  with zipfile.ZipFile(p)as z:
   require(len(z.namelist())==len(set(z.namelist())),'unique Jar members');images.append({n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()})
 require(images[0]==images[1]and sum(n.endswith('.class')for n in images[1])==74,'all Main/resources/debug same bytes required')
 value.update(coverage=counters,staticIssues=0,mainClasses=74,allMainResourcesDebugSameBytes=True,coverageXmlSha256=sha(cxml),staticSha256=sha(spots),jarSha256=sha(jar))
require(all(sha(source/n)==h for n,h in inputs.items()),'all fixed input bytes unchanged')
value['input']=INPUT;(out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));value['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(value))
'''


def main(before, retry_after_v2=False):
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'fixed clean source required')
    require(not subprocess.check_output(['git', 'diff', SOURCE, 'HEAD', '--', 'src/schubert-nk-storage/src/main', 'src/schubert-nk-storage/pom.xml', 'pom.xml'], cwd=ROOT), 'qualified Main/build unchanged required')
    full = json.loads((W / 'pg3304-directional-group-full-qualified-v1/manifest.safe.json').read_bytes())
    require(full['actualExit'] == 0 and full['result']['productionSource'] == SOURCE, 'qualified current-source whole required')
    stage = 'before' if before else 'after'
    if retry_after_v2:
        require(not before, 'only after failed environment may retry')
        old = json.loads((W / 'pg3326-storage-stream-after-v1/manifest.safe.json').read_bytes())
        require(old['actualExit'] == 1 and old['productionSource'] == SOURCE, 'preserved failed after-v1 required')
        require(subprocess.check_output(['git', 'show', old['testSource'] + ':' + TEST], cwd=ROOT) == (ROOT / TEST).read_bytes(), 'same corrected Test byte for environment-only retry')
    slot = 'PG3326-storage-stream-' + stage + ('-v2' if retry_after_v2 else '-v1')
    os.umask(0o077); out = W / slot.lower(); out.mkdir(mode=0o700)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    archive = out / 'source.tar'
    archive.write_bytes(subprocess.check_output(['git', 'archive', '--format=tar', head, 'pom.xml', 'mvnw', '.mvn', 'src', 'program/characterization', 'documents/100_RD', 'documents/200_UI', 'documents/300_SS'], cwd=ROOT))
    data = {'source': SOURCE, 'head': head, 'slot': slot, 'before': before, 'testPath': TEST,
            'archiveSha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'priorJarSha256': full['result']['jarHashes']['storage']}
    import inspect
    raw = 'INPUT=' + repr(data) + '\nMETHOD=' + repr(METHOD) + '\n' + inspect.getsource(require) + '\n' + inspect.getsource(classify) + '\n' + SERVER
    compile(raw, '<fixed Storage stream lifetime regression>', 'exec')
    script = out / 'regression.private.py'; script.write_text(raw)
    rc, _ = run('test ! -e ' + BASE + '/runs/' + slot + ' && test ! -e ' + BASE + '/source-' + slot + ' && mkdir -m700 ' + BASE + '/transfer/' + slot, timeout=30)
    require(rc == 0, 'new-only transport namespace required')
    for path in (archive, script):
        rc, _ = copy(path, BASE + '/transfer/' + slot + '/', timeout=60)
        require(rc == 0, 'fixed input transfer required')
    rc, output = run('python3 -B ' + shlex.quote(BASE + '/transfer/' + slot + '/regression.private.py'), timeout=360)
    (out / 'observer.private.log').write_text(output)
    receipt = {'actualExit': rc, 'testSource': head, 'productionSource': SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest()}
    if rc == 0:
        receipt['result'] = json.loads(next(x for x in output.splitlines() if x.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(receipt, sort_keys=True))
    print(json.dumps({k: v for k, v in receipt.items() if k != 'result'}))
    if rc == 0:
        print(json.dumps({k: v for k, v in receipt['result'].items() if k not in ('input', 'command', 'xmlHashes')}))
    return rc


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', action='store_true')
    parser.add_argument('--retry-after-v2', action='store_true')
    options = parser.parse_args()
    raise SystemExit(main(options.before, options.retry_after_v2))
