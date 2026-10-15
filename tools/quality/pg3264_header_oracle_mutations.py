"""Current Header Test counterexamples, private shadow classes/no agent/PT credit.

P001-01/UI232/SS322/451; before demonstrates, after rejects three fixed faults.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from lan_server import copy, run
from pg1446_current_cold_stage import W
from pg3258_statement_group_full_six import SOURCE, ROOT

BASE = '/home/mini/schubert-nk-pgpt'
PREFIX = 'src/schubert-nk-protocol/src/'
FILES = [PREFIX + 'test/java/dev/codex/schubert/nk/protocol/header/HeaderModelTest.java',
         *(PREFIX + 'main/java/dev/codex/schubert/nk/protocol/header/' + n + '.java'
           for n in ['CommonHeader', 'MessageKind', 'InteractionKind']),
         'tools/quality/vm/050_s1/HeaderOracleCanaryLauncher.java']

SERVER = r'''
import datetime,hashlib,json,os,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs'/INPUT['slot'];transfer=b/'transfer'/INPUT['slot'];source=b/'source-full-PG3248';repo=b/'m2/repository'
def require(v):
 if not v:raise ValueError('independent header oracle mutation refused')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out.mkdir(mode=0o700);start=datetime.datetime.now(datetime.timezone.utc).isoformat()
jar=source/'src/schubert-nk-protocol/target/schubert-nk-protocol-0.1.0-SNAPSHOT.jar';require(sha(jar)==INPUT['jarSha256'])
for n,h in INPUT['files'].items():require(sha(transfer/n)==h)
x=ET.parse(source/'src/schubert-nk-protocol/target/surefire-reports/TEST-dev.codex.schubert.nk.protocol.header.HeaderModelTest.xml').getroot();require(all(x.get(k)=='0'for k in ['failures','errors','skipped']))
props=[n.get('value')for n in x.findall('properties/property')if n.get('name')=='java.class.path'];require(len(props)==1);libs=[]
for e in props[0].split(':'):
 p=Path(e)
 if p.suffix=='.jar'and p.is_relative_to(repo):require(p.is_file()and p.resolve().is_relative_to(repo.resolve()));libs.append(p)
engines=[p for p in libs if p.name.startswith('junit-platform-engine-')];require(len(engines)==1);v=engines[0].parent.name
launcher=repo/'org/junit/platform/junit-platform-launcher'/v/('junit-platform-launcher-'+v+'.jar');require(launcher.is_file())
if launcher not in libs:libs.append(launcher)
hashes={str(p.relative_to(repo)):sha(p)for p in libs};cp=':'.join(map(str,[jar,*libs]));jdk=b/'tools/jdk-25.0.4/bin';env={k:v for k,v in os.environ.items()if k not in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS']}
structure='headerConstructorRejectsEveryStructuralViolation';enums='enumsMapOnlyApprovedWireValues'
vectors=[('BASE_STRUCTURE',structure,None,None,None),('BASE_ENUM',enums,None,None,None),('WRONG_EXCEPTION',structure,'CommonHeader','throw new LayoutValidationException("unsupported protocol identifier");','throw new NullPointerException("synthetic wrong type");'),('MESSAGE_WIRE',enums,'MessageKind',"RESPONSE('S')","RESPONSE('R')"),('INTERACTION_WIRE',enums,'InteractionKind',"SYNCHRONOUS('S')","SYNCHRONOUS('X')")]
results={}
for label,method,name,old,new in vectors:
 case=out/label;case.mkdir(mode=0o700);classes=case/'classes';classes.mkdir(mode=0o700)
 files=[transfer/'HeaderModelTest.java',transfer/'HeaderOracleCanaryLauncher.java']
 if name:
  raw=(transfer/(name+'.java')).read_text();require(raw.count(old)==1);shadow=case/(name+'.java');shadow.write_text(raw.replace(old,new));files.insert(0,shadow)
 c=subprocess.run([str(jdk/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*map(str,files)],env=env,capture_output=True,timeout=40)
 (case/'compile.private.log').write_bytes(c.stdout+c.stderr);require(c.returncode==0 and not c.stderr)
 r=subprocess.run([str(jdk/'java'),'-cp',str(classes)+':'+cp,'HeaderOracleCanaryLauncher',method],env=env,capture_output=True,timeout=30)
 (case/'test.private.log').write_bytes(r.stdout+r.stderr)
 reject=INPUT['phase']=='after'and name is not None
 require(r.returncode==(1 if reject else 0))
 require((b'CANARY_STARTED=1 SUCCEEDED=0 FAILED=1'if reject else b'CANARY_STARTED=1 SUCCEEDED=1 FAILED=0')in r.stdout)
 if reject:require(b'CANARY_FAILURE_CLASS=org.opentest4j.AssertionFailedError'in r.stdout)
 results[label]={'actualExit':r.returncode,'selectedTests':1,'logSha256':sha(case/'test.private.log'),'rejected':reject}
require(sha(jar)==INPUT['jarSha256']and all(sha(repo/k)==h for k,h in hashes.items()));require(not list(out.rglob('*.exec')))
value={'actualExit':0,'source':INPUT['source'],'testSource':INPUT['head'],'phase':INPUT['phase'],'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'vectors':results,'input':INPUT,'libraryHashes':hashes,'falseNegativesDemonstrated':3 if INPUT['phase']=='before'else 0,'mutationsRejected':3 if INPUT['phase']=='after'else 0,'productionChanged':False,'vmActions':0,'coverageCredit':0,'productionPtCredit':0,'formalAccepted':False}
(out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k not in ['input','libraryHashes']}))
'''


def main(phase):
    if phase not in ['before', 'after']:
        raise ValueError('fixed before/after phase required')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('fixed committed tool/Test required')
    if subprocess.check_output(['git', 'diff', SOURCE, 'HEAD', '--', *FILES[1:4]], cwd=ROOT):
        raise ValueError('unchanged real Production header required')
    full = json.loads((W / 'pg3250-cycle-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if full['actualExit'] != 0 or full['result']['tests'] != 3697 or full['result']['productionSource'] != SOURCE:
        raise ValueError('actual current3697 qualification required')
    slot = 'PG3264-header-oracle-' + phase + '-v1'
    data = {'source': SOURCE, 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'slot': slot, 'phase': phase, 'jarSha256': full['result']['jarHashes']['protocol'],
            'files': {Path(n).name: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in FILES}}
    raw = 'INPUT=' + repr(data) + '\n' + SERVER
    compile(raw, '<header shadow isolated mutations>', 'exec')
    os.umask(0o077); out = W / slot.lower(); out.mkdir(mode=0o700)
    script = out / 'mutations.private.py'; script.write_text(raw)
    code, _ = run(f'test ! -e {BASE}/runs/{slot} && test ! -e {BASE}/transfer/{slot} && mkdir -m700 {BASE}/transfer/{slot}', 30)
    if code:
        raise ValueError('new-only private header namespace required')
    for p in [*(ROOT / n for n in FILES), script]:
        code, _ = copy(p, f'{BASE}/transfer/{slot}/', 60)
        if code:
            raise ValueError('immutable header input transfer required')
    code, output = run(f'python3 -B {BASE}/transfer/{slot}/mutations.private.py', 300)
    (out / 'server.private.log').write_text(output)
    value = {'actualExit': code, 'source': SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if code == 0:
        value['result'] = json.loads(next(line for line in output.splitlines() if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value)); return code


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1]))
