"""Read-only original source; isolated shadow enum demonstrates oracle false negatives."""
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
SLOT = 'pg2630-result-oracle-canary-v1'
FILES = ['src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/header/HeaderModelTest.java',
         'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/header/ResultCode.java',
         'tools/quality/vm/050_s1/ResultCodeOracleCanaryLauncher.java']
SERVER = r'''
import datetime,hashlib,json,os,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG2630-canary-v1';transfer=b/'transfer/PG2630-canary-v1';source=b/'source-full-PG2600'
def require(v):
 if not v:raise ValueError('isolated original oracle canary refused')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out.mkdir(mode=0o700);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
jar=source/'src/schubert-nk-protocol/target/schubert-nk-protocol-0.1.0-SNAPSHOT.jar';require(sha(jar)==INPUT['jarSha256'])
for name,h in INPUT['files'].items():require(sha(transfer/name)==h)
xml=source/'src/schubert-nk-protocol/target/surefire-reports/TEST-dev.codex.schubert.nk.protocol.header.HeaderModelTest.xml'
x=ET.parse(xml).getroot();require(x.get('failures')=='0' and x.get('errors')=='0' and x.get('skipped')=='0')
properties=[n.get('value')for n in x.findall('properties/property')if n.get('name')=='java.class.path'];require(len(properties)==1)
repo=b/'m2/repository';libs=[]
for entry in properties[0].split(':'):
 p=Path(entry)
 if p.suffix=='.jar' and p.is_relative_to(repo):
  require(p.is_file() and p.resolve().is_relative_to(repo.resolve()));libs.append(p)
launcher=repo/'org/junit/platform/junit-platform-launcher/6.0.3/junit-platform-launcher-6.0.3.jar'
if not launcher.exists():
 choices=list((repo/'org/junit/platform/junit-platform-launcher').glob('*/*.jar'));require(len(choices)==1);launcher=choices[0]
if launcher not in libs:libs.append(launcher)
library_hashes={str(p.relative_to(repo)):sha(p)for p in libs};require(any('junit-platform-launcher/'in k for k in library_hashes))
cp=':'.join(map(str,[jar,*libs]));jdk=b/'tools/jdk-25.0.4/bin';env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS')}
original=(transfer/'ResultCode.java').read_text();vectors={'ORIGINAL':original}
for label,old,new in [('ADDED','RESOURCE_LIMIT("9001", false);','RESOURCE_LIMIT("9001", false),\n  UNAPPROVED_CANARY("9900", false);'),('WIRE','AUTHENTICATION_FAILED("0101", false)','AUTHENTICATION_FAILED("0199", false)'),('PROFILE','AUTHENTICATION_FAILED("0101", false)','AUTHENTICATION_FAILED("0101", true)')]:
 require(original.count(old)==1);vectors[label]=original.replace(old,new)
results={}
for label,text in vectors.items():
 case=out/label;case.mkdir(mode=0o700);classes=case/'classes';classes.mkdir(mode=0o700);shadow=case/'ResultCode.java';shadow.write_text(text)
 compile_run=subprocess.run([str(jdk/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(shadow),str(transfer/'HeaderModelTest.java'),str(transfer/'ResultCodeOracleCanaryLauncher.java')],env=env,capture_output=True,timeout=40)
 (case/'compile.private.log').write_bytes(compile_run.stdout+compile_run.stderr);require(compile_run.returncode==0 and not compile_run.stderr)
 result=subprocess.run([str(jdk/'java'),'-cp',str(classes)+':'+cp,'ResultCodeOracleCanaryLauncher'],env=env,capture_output=True,timeout=30)
 (case/'test.private.log').write_bytes(result.stdout+result.stderr);require(result.returncode==0 and b'CANARY_STARTED=1 SUCCEEDED=1 FAILED=0'in result.stdout)
 results[label]={'actualExit':result.returncode,'syntheticSourceSha256':sha(shadow),'logSha256':sha(case/'test.private.log')}
require(sha(jar)==INPUT['jarSha256'] and all(sha(repo/k)==h for k,h in library_hashes.items()))
require(not list(out.rglob('*.exec')))
value={'actualExit':0,'source':INPUT['source'],'testSource':INPUT['head'],'startUTC':started,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'falseNegativesDemonstrated':3,'vectors':results,'libraryHashes':library_hashes,'input':INPUT,'vmActions':0,'productionChanged':False,'coverageCredit':0,'productionPtCredit':0,'formalAccepted':False}
(out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k not in('input','libraryHashes','vectors')}))
'''


def main():
    full = json.loads((W / 'pg2601-retention-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if full['actualExit'] != 0 or full['result']['productionSource'] != SOURCE:
        raise ValueError('actual unchanged production Main required')
    if subprocess.check_output(['git', 'diff', SOURCE, '--', *FILES[:2]]):
        raise ValueError('original uncorrected code and test required')
    inputs = {'source': SOURCE, 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
              'jarSha256': full['result']['jarHashes']['protocol'],
              'files': {Path(n).name: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in FILES}}
    code = 'INPUT=' + repr(inputs) + '\n' + SERVER
    compile(code, '<isolated false negative canary>', 'exec')
    os.umask(0o077);out = W / SLOT;out.mkdir(mode=0o700)
    script = out / 'canary.private.py';script.write_text(code)
    c, _ = run('test ! -e ' + BASE + '/runs/PG2630-canary-v1 && test ! -e ' + BASE + '/transfer/PG2630-canary-v1 && mkdir -m700 ' + BASE + '/transfer/PG2630-canary-v1', 30)
    if c:raise ValueError('fresh synthetic namespace required')
    for p in [*(ROOT / n for n in FILES), script]:
        c, _ = copy(p, BASE + '/transfer/PG2630-canary-v1/', 60)
        if c:raise ValueError('immutable canary transfer required')
    c, output = run('python3 -B ' + BASE + '/transfer/PG2630-canary-v1/canary.private.py', 180)
    (out / 'server.private.log').write_text(output)
    value = {'actualExit': c, 'source': SOURCE, 'payloadSha256': hashlib.sha256(code.encode()).hexdigest(), 'formalAccepted': False}
    if not c:value['result'] = json.loads(next(x for x in output.splitlines() if x.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return c


if __name__ == '__main__':
    raise SystemExit(main())
