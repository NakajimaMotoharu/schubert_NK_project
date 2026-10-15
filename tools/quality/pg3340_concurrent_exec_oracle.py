"""Private actual concurrent exec common-wrong-vector diagnosis, no source/runtime mutation."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys

from lan_server import copy, run
from pg3294_protocol_directional_oracle import require, fixed_jdk, launcher_path
from pg3274_header_group_full_six import ROOT, SOURCE, W

BASE = '/home/mini/schubert-nk-pgpt'
PREFIX = 'src/schubert-nk-storage/src/'
FILES = [PREFIX + 'test/java/dev/codex/schubert/nk/storage/LinuxProcessExecTest.java',
         PREFIX + 'main/java/dev/codex/schubert/nk/storage/LinuxProcessExec.java',
         'tools/quality/vm/050_s1/ExecOracleCanaryLauncher.java']


def mutate(raw):
    anchor = 'if (argv.isEmpty() || argv.size() > 64 || env.size() > 32) throw invalid();'
    require(raw.count(anchor) == 1 and 'PRIVATE_COMMON_WRONG' not in raw, 'one actual vector validation anchor required')
    injected = '''if (!argv.isEmpty() && argv.getFirst().startsWith("fixture")) {
      argv = List.of("PRIVATE_COMMON_WRONG");
      env.clear();
      env.put("X", "PRIVATE_COMMON_WRONG");
    }
    '''
    return raw.replace(anchor, injected + anchor)


SERVER = r'''
import datetime,hashlib,json,os,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
os.umask(0o077);B=Path('/home/mini/schubert-nk-pgpt');T=B/'source-full-PG3302/src/schubert-nk-storage/target';I=B/'transfer'/INPUT['slot'];O=B/'runs'/INPUT['slot'];O.mkdir(mode=0o700)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();jar=T/'schubert-nk-storage-0.1.0-SNAPSHOT.jar';require(sha(jar)==INPUT['jarSha256'],'qualified actual Storage jar required')
for n,h in INPUT['files'].items():require(sha(I/n)==h,'fixed input byte required')
x=ET.parse(T/'surefire-reports/TEST-dev.codex.schubert.nk.storage.LinuxProcessExecTest.xml').getroot();props=[p.get('value')for p in x.findall('properties/property')if p.get('name')=='java.class.path'];require(len(props)==1,'one original classpath required')
repo=B/'m2/repository';libs=[]
for entry in props[0].split(os.pathsep):
 p=Path(entry)
 if p.suffix=='.jar'and p!=jar:
  require(p.is_file()and p.resolve().is_relative_to(repo.resolve()),'qualified fixed repo library required');libs.append(p)
launcher=launcher_path([p for p in libs if p.name.startswith('junit-platform-engine-')],repo);require(launcher.is_file()and launcher.resolve().is_relative_to(repo.resolve()),'same-version actual launcher required')
if launcher not in libs:libs.append(launcher)
hashes={str(p):sha(p)for p in libs};cp=os.pathsep.join([str(jar),str(T/'test-classes'),*map(str,libs)]);homes=[p.get('value')for p in x.findall('properties/property')if p.get('name')=='java.home'];J=fixed_jdk(homes,B)
env={k:v for k,v in os.environ.items()if k not in['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS']};env['JAVA_HOME']=str(J.parent);env['TZ']='Asia/Tokyo'
version=subprocess.run([str(J/'java'),'--version'],env=env,capture_output=True,timeout=20);require(version.returncode==0 and b'25.0.4'in version.stdout,'actual fixed Java25 required')
start=datetime.datetime.now(datetime.timezone.utc).isoformat();results={}
for label,selector,wrong in [('NORMAL_LITERAL','opsExec001LiteralVectorsAndArenaLifetime',False),('NORMAL_CONCURRENT','opsExec007ConcurrentInputsRemainIndependent',False),('COMMON_WRONG_CONCURRENT','opsExec007ConcurrentInputsRemainIndependent',True)]:
 case=O/label;case.mkdir(mode=0o700);classes=case/'classes';classes.mkdir(mode=0o700);files=[I/'LinuxProcessExecTest.java',I/'ExecOracleCanaryLauncher.java']
 if wrong:
  shadow=case/'LinuxProcessExec.java';shadow.write_text(mutate((I/'LinuxProcessExec.java').read_text()));files.insert(0,shadow)
 c=subprocess.run([str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*map(str,files)],env=env,capture_output=True,timeout=45);(case/'compile.private.log').write_bytes(c.stdout+c.stderr);require(c.returncode==0 and not c.stderr,'clean actual compiler required')
 r=subprocess.run([str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',os.pathsep.join([str(classes),cp]),'ExecOracleCanaryLauncher',selector],env=env,capture_output=True,timeout=45);(case/'test.private.log').write_bytes(r.stdout+r.stderr)
 reject=wrong and INPUT['phase']=='after';require(r.returncode==(1 if reject else 0),'actual expected selected JUnit result required');require((b'CANARY_STARTED=1 SUCCEEDED=0 FAILED=1'if reject else b'CANARY_STARTED=1 SUCCEEDED=1 FAILED=0')in r.stdout,'one genuine selected method required')
 if reject:require(b'CANARY_ASSERTION_CAUSE=true'in r.stdout,'meaningful independent assertion must reject, not environment failure')
 results[label]={'actualExit':r.returncode,'selector':selector,'rejected':reject,'compileLogSha256':sha(case/'compile.private.log'),'testLogSha256':sha(case/'test.private.log')}
require(sha(jar)==INPUT['jarSha256']and all(sha(Path(p))==h for p,h in hashes.items()),'all actual artifact and libraries preserved');require(not list(O.rglob('*.exec')),'no agent coverage credit')
value={'actualExit':0,'productionSource':INPUT['source'],'testSource':INPUT['head'],'phase':INPUT['phase'],'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'vectors':results,'falseNegatives':1 if INPUT['phase']=='before'else 0,'mutationsRejected':1 if INPUT['phase']=='after'else 0,'productionChanged':False,'vmActions':0,'newPtCredit':0,'coverageCredit':0,'formalUpdated':False,'input':INPUT,'libraryHashes':hashes}
(O/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k not in['input','libraryHashes']}))
'''


def main(phase):
    require(phase in ('before', 'after'), 'explicit phase required')
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'fixed clean source required')
    require(not subprocess.check_output(['git', 'diff', SOURCE, 'HEAD', '--', FILES[1]], cwd=ROOT), 'actual Main unchanged required')
    full = json.loads((W / 'pg3304-directional-group-full-qualified-v1/manifest.safe.json').read_bytes())
    require(full['actualExit'] == 0 and full['result']['productionSource'] == SOURCE, 'qualified actual current Main full required')
    slot = 'PG3340-exec-oracle-' + phase + '-v1'
    data = {'source': SOURCE, 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'slot': slot, 'phase': phase,
            'jarSha256': full['result']['jarHashes']['storage'], 'files': {Path(p).name: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in FILES}}
    raw = 'INPUT=' + repr(data) + '\n' + '\n'.join(inspect.getsource(f) for f in [require, mutate, fixed_jdk, launcher_path]) + '\n' + SERVER
    compile(raw, '<private independent exec oracle diagnosis>', 'exec')
    os.umask(0o077); out = W / slot.lower(); out.mkdir(mode=0o700); script = out / 'oracle.private.py'; script.write_text(raw)
    code, _ = run(f'test ! -e {BASE}/runs/{slot} && test ! -e {BASE}/transfer/{slot} && mkdir -m700 {BASE}/transfer/{slot}', timeout=30); require(code == 0, 'new-only diagnostic slot required')
    for path in [*(ROOT / f for f in FILES), script]:
        code, _ = copy(path, f'{BASE}/transfer/{slot}/', timeout=60); require(code == 0, 'fixed diagnostic transfer required')
    code, output = run(f'python3 -B {BASE}/transfer/{slot}/oracle.private.py', timeout=240); (out / 'observer.private.log').write_text(output)
    value = {'actualExit': code, 'productionSource': SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalUpdated': False}
    if code == 0:
        value['result'] = json.loads(next(line for line in output.splitlines() if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return code


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1] if len(sys.argv) == 2 else ''))
