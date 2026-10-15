"""Actual seven-suite/44-case current Test group; same six-module Main, no runtime action."""
import hashlib
import inspect
import json
import os
import shlex
import subprocess

from lan_server import copy, run
from pg3330_stream_group_integration import ROOT, SOURCE, W, engine

CLASSES = {
    'protocol': {'dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest': 7,
                 'dev.codex.schubert.nk.protocol.file.MediaDescriptorValidatorTest': 7},
    'storage': {'dev.codex.schubert.nk.storage.LinuxProcessExecTest': 8},
    'bootstrap': {'dev.codex.schubert.nk.bootstrap.FixedNativeCoverageProfileTest': 5},
    'api': {'dev.codex.schubert.nk.api.security.LoginUsernameTest': 3},
    'web': {'dev.codex.schubert.nk.web.media.HttpByteRangeParserTest': 4},
    'batch': {'dev.codex.schubert.nk.batch.platform.MorningStopPassTest': 10}}
CHANGED = {
    'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/LinuxProcessExecTest.java',
    'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/file/LargeResultRecordCodecTest.java',
    'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/file/MediaDescriptorValidatorTest.java',
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MorningStopPassTest.java'}
BASE = '/home/mini/schubert-nk-pgpt'


def require(value, message):
    if not value:
        raise ValueError(message)


def classify(roots, expected):
    require(len(roots) == len(expected), 'exact selected suite count required')
    cases = set(); names = set()
    for root in roots:
        name = root.get('name'); require(name in expected and name not in names, 'exact unique selected class')
        names.add(name); actual = root.findall('testcase')
        require(int(root.get('tests')) == len(actual) == expected[name], 'actual selected cases required')
        require(all(root.get(k) == '0' for k in ['failures', 'errors', 'skipped']), 'no failed/error/skipped')
        require(not any('rerun' in n.tag.lower() or 'flaky' in n.tag.lower() or n.tag in ['failure', 'error', 'skipped'] for n in root.iter()), 'no hidden failure or retry')
        for case in actual:
            identity = (case.get('classname'), case.get('name'))
            require(identity[0] == name and identity not in cases, 'unique original case identities')
            cases.add(identity)
    require(names == set(expected), 'no selected class omitted')
    return cases


def validate(snapshot):
    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT)
    full = json.loads((W / 'pg3332-stream-group-full-qualified-v1/manifest.safe.json').read_bytes())
    native = json.loads((W / 'pg3334-stream-group-native-qualified-v1/manifest.safe.json').read_bytes())
    require(full['actualExit'] == native['actualExit'] == 0 and full['result']['productionSource'] == SOURCE, 'previous whole/native genuinely complete')
    changed = set(git('diff', '--name-only', full['result']['sourceSnapshot'], snapshot, '--', *engine.SCOPE).decode().splitlines())
    require(changed == CHANGED, 'exact four Test-only changes, no Main/settings/resource changes')
    for slot, test in [('pg3340-exec-oracle-after-v1', 'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/LinuxProcessExecTest.java'),
                       ('pg3346-large-result-oracle-after-v1', 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/file/LargeResultRecordCodecTest.java')]:
        p = W / slot; receipt = json.loads((p / 'manifest.safe.json').read_bytes()); payload = (p / 'oracle.private.py').read_bytes()
        require(hashlib.sha256(payload).hexdigest() == receipt['payloadSha256'], 'immutable diagnostic payload required')
        result = receipt['result']
        require(receipt['actualExit'] == result['actualExit'] == result['falseNegatives'] == 0 and result['mutationsRejected'] == 1
                and result['phase'] == 'after' and result['productionSource'] == SOURCE, 'actual normal and wrong rejection required')
        require(git('show', snapshot + ':' + test) == git('show', result['testSource'] + ':' + test), 'exact independently tested oracle source required')
    return full['result']


SERVER = r'''
import datetime,hashlib,json,os,shutil,subprocess,tarfile,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
os.umask(0o077);B=Path('/home/mini/schubert-nk-pgpt');O=B/'runs/PG3348-related-v1';S=B/'source-PG3348-related-v1';I=B/'transfer/PG3348-related-v1';require(shutil.disk_usage(B).free>12*1024**3,'2GiB work plus10GiB preservation capacity required');O.mkdir(mode=0o700);S.mkdir(mode=0o700)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();archive=I/'source.tar';require(sha(archive)==INPUT['archiveSha256'],'fixed archive required')
with tarfile.open(archive)as t:t.extractall(S,filter='data')
inputs={str(p.relative_to(S)):sha(p)for p in S.rglob('*')if p.is_file()};env={k:v for k,v in os.environ.items()if k not in['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS']};env['JAVA_HOME']=str(B/'tools/jdk-25.0.4');env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
args=[str(B/'tools/maven/bin/mvn'),'-o','--no-transfer-progress','-Dstyle.color=never','-Djansi.force=false','-Dmaven.repo.local='+str(B/'m2/repository'),'-Dnk.pt.repository='+str(S),'-Dtest='+','.join(n for classes in INPUT['classes'].values()for n in classes),'-pl',','.join('src/schubert-nk-'+m for m in INPUT['classes']),'clean','spotless:check','test-compile','jar:test-jar','test','spotbugs:check','jacoco:report','jar:jar']
start=datetime.datetime.now(datetime.timezone.utc).isoformat();begin={'source':INPUT['source'],'sourceSnapshot':INPUT['head'],'pid':os.getpid(),'ticks':int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'startUTC':start,'archiveSha256':INPUT['archiveSha256'],'expectedTests':44,'expectedSuites':7,'vmActions':0};(O/'begin.safe.json').write_text(json.dumps(begin,sort_keys=True));print(json.dumps({'started':begin}),flush=True)
with(O/'maven.private.log').open('xb')as f:r=subprocess.run(args,cwd=S,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900,umask=0o027)
(O/'maven-exit.safe.json').write_text(json.dumps({'mavenExit':r.returncode,'source':INPUT['source'],'snapshot':INPUT['head'],'command':args}));require(r.returncode==0,'genuine selected Maven0 required')
result={};all_cases=set();members=0
for module,expected in INPUT['classes'].items():
 T=S/('src/schubert-nk-'+module+'/target');xmls=sorted((T/'surefire-reports').glob('TEST-*.xml'));cases=classify([ET.parse(p).getroot()for p in xmls],expected);all_cases.update(cases)
 spots=T/'spotbugsXml.xml';require(not ET.parse(spots).getroot().findall('.//BugInstance'),'static0 required');coverage=T/'site/jacoco/jacoco.xml';node=ET.parse(coverage).getroot();counters={x.get('type'):{'missed':int(x.get('missed')),'covered':int(x.get('covered'))}for x in node.findall('counter')}
 jar=T/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar');old=B/('source-full-PG3330/src/schubert-nk-'+module+'/target/schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar');require(sha(old)==INPUT['priorJarHashes'][module],'qualified prior Jar required');images=[]
 for p in(old,jar):
  with zipfile.ZipFile(p)as z:
   require(len(z.namelist())==len(set(z.namelist())),'unique all Jar members');images.append({n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()})
 require(images[0]==images[1],'every Main/resource/debug member identical required');physical=sum(n.endswith('.class')for n in images[1]);members+=physical
 result[module]={'tests':len(cases),'suites':len(xmls),'mainClasses':physical,'staticIssues':0,'coverage':counters,'xmlHashes':{p.name:sha(p)for p in xmls},'coverageXmlSha256':sha(coverage),'staticSha256':sha(spots),'jarSha256':sha(jar)}
 if module=='batch':
  target=next(c for p in node.findall('package')for c in p.findall('class')if c.get('name')=='dev/codex/schubert/nk/batch/platform/MorningStopPass');method=next(n for n in target.findall('method')if n.get('name')=='pausePreservingInterrupt');result[module]['pauseMethodCounters']={x.get('type'):{'missed':int(x.get('missed')),'covered':int(x.get('covered'))}for x in method.findall('counter')}
require(len(all_cases)==44 and members==1643,'all44 actual cases/all1643 physical Main required')
for expected in [('dev.codex.schubert.nk.protocol.file.MediaDescriptorValidatorTest','utf8MaximumFieldsAndN12UseIndependentCanonicalBoundaries'),('dev.codex.schubert.nk.batch.platform.MorningStopPassTest','mpass010NewInterruptDuringUnknownPreservesFlagAndAllTerminalObservations')]:require(expected in all_cases,'both actual new methods required')
require(all(sha(S/n)==h for n,h in inputs.items()),'all fixed source inputs unchanged');value={'actualExit':0,'mavenExit':r.returncode,'productionSource':INPUT['source'],'sourceSnapshot':INPUT['head'],'sourceArchiveSha256':INPUT['archiveSha256'],'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tests':44,'suites':7,'mainClasses':members,'staticSixModules':0,'FESFlakyNotRun':0,'modules':result,'allMainResourcesDebugSameBytes':True,'logSha256':sha(O/'maven.private.log'),'fullSixIntegrationPending':True,'vmActions':0,'formalUpdated':False,'newMethods':2,'input':INPUT}
(O/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));value['serverManifestSha256']=sha(O/'manifest.safe.json');print(json.dumps(value))
'''


def main():
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'fixed clean source required')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(); full = validate(head)
    os.umask(0o077); out = W / 'pg3348-related-boundary-group-v1'; out.mkdir(mode=0o700); archive = out / 'source.tar'
    archive.write_bytes(subprocess.check_output(['git', 'archive', '--format=tar', head, 'pom.xml', 'mvnw', '.mvn', 'src', 'program/characterization', 'documents/100_RD', 'documents/200_UI', 'documents/300_SS'], cwd=ROOT))
    inputs = {'source': SOURCE, 'head': head, 'archiveSha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'classes': CLASSES, 'priorJarHashes': full['jarHashes']}
    raw = 'INPUT=' + repr(inputs) + '\n' + inspect.getsource(require) + '\n' + inspect.getsource(classify) + '\n' + SERVER
    compile(raw, '<fixed related44 across six modules>', 'exec'); script = out / 'related.private.py'; script.write_text(raw)
    rc, _ = run('test ! -e ' + BASE + '/runs/PG3348-related-v1 && test ! -e ' + BASE + '/source-PG3348-related-v1 && mkdir -m700 ' + BASE + '/transfer/PG3348-related-v1', timeout=30); require(rc == 0, 'new-only related scope required')
    for path in (archive, script):
        rc, _ = copy(path, BASE + '/transfer/PG3348-related-v1/', timeout=60); require(rc == 0, 'fixed related input transfer required')
    rc, output = run('python3 -B ' + shlex.quote(BASE + '/transfer/PG3348-related-v1/related.private.py'), timeout=960); (out / 'observer.private.log').write_text(output)
    value = {'actualExit': rc, 'productionSource': SOURCE, 'testSource': head, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalUpdated': False}
    if rc == 0:
        value['result'] = json.loads([line for line in output.splitlines() if line.startswith('{')][-1])
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps({k: v for k, v in value.items() if k != 'result'}))
    if rc == 0:
        print(json.dumps({k: v for k, v in value['result'].items() if k not in ('input', 'modules')}))
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
