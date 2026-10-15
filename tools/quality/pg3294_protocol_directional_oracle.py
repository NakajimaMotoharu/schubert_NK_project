"""Private normal/stable-wrong-output and reciprocal DTO swap counterexamples.

No real source/jar mutation, agent, business execution, PT or coverage credit.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from lan_server import copy, run
from pg3274_header_group_full_six import ROOT, SOURCE, W

BASE = '/home/mini/schubert-nk-pgpt'
PREFIX = 'src/schubert-nk-protocol/src/'
FILES = [PREFIX + 'test/java/dev/codex/schubert/nk/protocol/layout/PayloadTypeCatalogTest.java',
         PREFIX + 'test/java/dev/codex/schubert/nk/protocol/codec/PayloadGoldenVectorTest.java',
         PREFIX + 'main/java/dev/codex/schubert/nk/protocol/layout/auth/LoginRequestData.java',
         PREFIX + 'main/java/dev/codex/schubert/nk/protocol/codec/PayloadCodec.java',
         'tools/quality/vm/050_s1/ProtocolOracleCanaryLauncher.java']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def swap_once(raw, left, right):
    require(raw.count(left) == raw.count(right) == 1 and '__PG3294_SWAP__' not in raw, 'two exact independent mutation anchors required')
    return raw.replace(left, '__PG3294_SWAP__').replace(right, left).replace('__PG3294_SWAP__', right)


def mutate_dto(raw):
    for left, right in [
        ('TypedFieldValues.requiredString(fields, "Username")', 'TypedFieldValues.requiredString(fields, "Password")'),
        ('Map.entry("Username", TypedFieldValues.text(username))', 'Map.entry("Password", TypedFieldValues.text(password))')]:
        # Swap references only, retaining each wire field name in fields().
        if left.startswith('Map.entry'):
            require(raw.count(left) == raw.count(right) == 1, 'exact directional encode anchors required')
            raw = raw.replace(left, 'Map.entry("Username", TypedFieldValues.text(password))').replace(right, 'Map.entry("Password", TypedFieldValues.text(username))')
        else:
            raw = swap_once(raw, left, right)
    return raw


def mutate_bytes(raw):
    anchor = 'return new FixedPayload(data, fields.layout().recordLength(), records);'
    require(raw.count(anchor) == 1, 'exact stable output mutation anchor required')
    return raw.replace(anchor, "if (data.length > 0) data[0] = (byte) 'X';\n    " + anchor)


SERVER = r'''
import datetime,hashlib,json,os,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
os.umask(0o077)
B=Path('/home/mini/schubert-nk-pgpt');S=B/'source-full-PG3274';T=S/'src/schubert-nk-protocol/target';I=B/'transfer'/INPUT['slot'];O=B/'runs'/INPUT['slot']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
O.mkdir(mode=0o700);start=datetime.datetime.now(datetime.timezone.utc).isoformat()
jar=T/'schubert-nk-protocol-0.1.0-SNAPSHOT.jar'
require(sha(jar)==INPUT['jarSha256'],'immutable qualified protocol jar required')
for name,digest in INPUT['files'].items():require(sha(I/name)==digest,'fixed transferred source required')
x=ET.parse(T/'surefire-reports/TEST-dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest.xml').getroot()
props=[p.get('value')for p in x.findall('properties/property')if p.get('name')=='java.class.path'];require(len(props)==1,'exact existing actual classpath required')
libs=[Path(p)for p in props[0].split(os.pathsep)if p.endswith('.jar')and Path(p).is_file()and Path(p)!=jar]
hashes={str(p):sha(p)for p in libs};require(libs,'real qualified libraries required')
cp=os.pathsep.join([str(jar),str(T/'test-classes'),*map(str,libs)])
jdk=B/'toolchain/jdk-25.0.4/bin';env=os.environ.copy();env['JAVA_HOME']=str(jdk.parent);env['TZ']='Asia/Tokyo';env.pop('JAVA_TOOL_OPTIONS',None);env.pop('JDK_JAVA_OPTIONS',None)
type_selector='layout.PayloadTypeCatalogTest#'+('allSixtyFourLayoutsRoundTripThroughSixtyNineExplicitNamedTypes'if INPUT['phase']=='before'else'namedLoginFieldsHaveIndependentDirectionalMeaning')
parallel='codec.PayloadGoldenVectorTest#sharedCodecProducesIdenticalBytesUnderConcurrentUse'
vectors=[('NORMAL_TYPE',type_selector,None,None),('DTO_RECIPROCAL_SWAP',type_selector,'LoginRequestData',mutate_dto),('NORMAL_CONCURRENT',parallel,None,None),('STABLE_WRONG_BYTES',parallel,'PayloadCodec',mutate_bytes)]
results={}
for label,selector,name,mutator in vectors:
 case=O/label;case.mkdir(mode=0o700);classes=case/'classes';classes.mkdir(mode=0o700)
 files=[I/'PayloadTypeCatalogTest.java',I/'PayloadGoldenVectorTest.java',I/'ProtocolOracleCanaryLauncher.java']
 if name:
  shadow=case/(name+'.java');shadow.write_text(mutator((I/(name+'.java')).read_text()));files.insert(0,shadow)
 c=subprocess.run([str(jdk/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*map(str,files)],env=env,capture_output=True,timeout=45)
 (case/'compile.private.log').write_bytes(c.stdout+c.stderr);require(c.returncode==0 and not c.stderr,'clean actual compiler required')
 r=subprocess.run([str(jdk/'java'),'-cp',str(classes)+os.pathsep+cp,'ProtocolOracleCanaryLauncher',selector],env=env,capture_output=True,timeout=45)
 (case/'test.private.log').write_bytes(r.stdout+r.stderr)
 reject=INPUT['phase']=='after'and name is not None
 require(r.returncode==(1 if reject else 0),'actual JUnit counterexample result required')
 require((b'CANARY_STARTED=1 SUCCEEDED=0 FAILED=1'if reject else b'CANARY_STARTED=1 SUCCEEDED=1 FAILED=0')in r.stdout,'one actual case summary required')
 if reject:require(b'CANARY_FAILURE_CLASS=org.opentest4j.AssertionFailedError'in r.stdout,'oracle must reject by meaningful assertion')
 results[label]={'actualExit':r.returncode,'rejected':reject,'logSha256':sha(case/'test.private.log'),'selector':selector}
require(sha(jar)==INPUT['jarSha256']and all(sha(Path(p))==h for p,h in hashes.items()),'real artifact/library preservation required')
require(not list(O.rglob('*.exec')),'no agent/native coverage credit')
value={'actualExit':0,'productionSource':INPUT['source'],'testSource':INPUT['head'],'phase':INPUT['phase'],'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'vectors':results,'falseNegatives':2 if INPUT['phase']=='before'else 0,'mutationsRejected':2 if INPUT['phase']=='after'else 0,'productionChanged':False,'vmActions':0,'newPtCredit':0,'coverageCredit':0,'formalUpdated':False,'input':INPUT,'libraryHashes':hashes}
(O/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k not in ['input','libraryHashes']}))
'''


def main(phase):
    import inspect
    require(phase in ('before', 'after'), 'explicit before/after phase required')
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'fixed clean tool/Test source required')
    require(not subprocess.check_output(['git', 'diff', SOURCE, 'HEAD', '--', *FILES[2:4]], cwd=ROOT), 'real Production unchanged required')
    full = json.loads((W / 'pg3276-header-group-full-qualified-v1/manifest.safe.json').read_bytes())
    require(full['actualExit'] == 0 and full['result']['productionSource'] == SOURCE and full['result']['tests'] == 3701, 'completed actual3701 required')
    slot = 'PG3294-directional-oracle-' + phase + '-v1'
    data = {'source': SOURCE, 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'slot': slot, 'phase': phase, 'jarSha256': full['result']['jarHashes']['protocol'],
            'files': {Path(p).name: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in FILES}}
    raw = 'INPUT=' + repr(data) + '\n' + '\n'.join(inspect.getsource(f) for f in [require, swap_once, mutate_dto, mutate_bytes]) + '\n' + SERVER
    compile(raw, '<private protocol oracle counterexamples>', 'exec')
    os.umask(0o077); out = W / slot.lower(); out.mkdir(mode=0o700)
    script = out / 'oracle.private.py'; script.write_text(raw)
    rc, _ = run(f'test ! -e {BASE}/runs/{slot} && test ! -e {BASE}/transfer/{slot} && mkdir -m700 {BASE}/transfer/{slot}', 30)
    require(rc == 0, 'new-only private server slot required')
    for path in [*(ROOT / n for n in FILES), script]:
        rc, _ = copy(path, f'{BASE}/transfer/{slot}/', 60); require(rc == 0, 'exact immutable transfer required')
    rc, output = run(f'python3 -B {BASE}/transfer/{slot}/oracle.private.py', 300)
    (out / 'observer.private.log').write_text(output)
    value = {'actualExit': rc, 'productionSource': SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalUpdated': False}
    if rc == 0:
        value['result'] = json.loads(next(line for line in output.splitlines() if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return rc


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1] if len(sys.argv) == 2 else ''))
