"""Read-only whole frozen Main call references. Zero references is not unreachable acceptance."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy, run
from pg1446_current_cold_stage import W
from pg2510_strict_reference_full_six import SOURCE

ROOT = Path(__file__).resolve().parents[2]
BASE = '/home/mini/schubert-nk-pgpt'
SLOT = 'pg2584-factory-references-v1'
FILE = 'tools/quality/vm/050_s1/Pg2584MorningFactoryReferences.java'
ASM = 'org/ow2/asm/asm/9.10.1/asm-9.10.1.jar'


def main():
    os.umask(0o077)
    full = json.loads((W / 'pg2511-strict-reference-full-qualified-v1/manifest.safe.json').read_bytes())
    if type(full.get('actualExit')) is not int or full['actualExit'] != 0 or full['result']['productionSource'] != SOURCE:
        raise ValueError('actual whole current Main required')
    source = ROOT / FILE
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    asm_sha = hashlib.sha256((ROOT.parent / 'toolchain/m2/repository' / ASM).read_bytes()).hexdigest()
    out = W / SLOT
    out.mkdir(mode=0o700)
    c, _ = run('test ! -e ' + BASE + '/runs/PG2584-v1 && mkdir -m700 ' + BASE + '/runs/PG2584-v1', 30)
    if c:
        raise ValueError('one fresh read-only audit namespace required')
    c, _ = copy(source, BASE + '/runs/PG2584-v1/', 30)
    if c:
        raise ValueError('fixed audit source transfer required')
    script = '''import hashlib,json,pathlib,subprocess
b=pathlib.Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG2584-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(v):
 if not v:raise ValueError('whole immutable audit input refused')
java=out/'Pg2584MorningFactoryReferences.java';asm=b/'m2/repository'/ASM
require(sha(java)==JAVA_SHA and sha(asm)==ASM_SHA)
jars=[]
for module,h in JAR_HASHES.items():
 p=b/'source-full-PG2510/src'/('schubert-nk-'+module)/'target'/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
 require(sha(p)==h);jars.append(p)
classes=out/'classes';classes.mkdir(mode=0o700);jdk=b/'tools/jdk-25.0.4/bin'
c=subprocess.run([str(jdk/'javac'),'-Xlint:all','-Werror','-cp',str(asm),'-d',str(classes),str(java)],capture_output=True,timeout=30)
(out/'compile.private.log').write_bytes(c.stdout+c.stderr);require(c.returncode==0 and not c.stderr)
r=subprocess.run([str(jdk/'java'),'-cp',str(classes)+':'+str(asm),'Pg2584MorningFactoryReferences',*[str(p)for p in jars]],capture_output=True,timeout=60)
(out/'references.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stderr)
require(all(sha(p)==h for p,h in zip(jars,JAR_HASHES.values())) and sha(java)==JAVA_SHA and sha(asm)==ASM_SHA)
print(r.stdout.decode())
'''
    inputs = {'ASM': ASM, 'ASM_SHA': asm_sha, 'JAVA_SHA': sha, 'JAR_HASHES': full['result']['jarHashes']}
    code = '\n'.join(k + '=' + repr(v) for k, v in inputs.items()) + '\n' + script
    compile(code, '<fixed whole audit execution>', 'exec')
    command = out / 'audit.private.py'
    command.write_text(code)
    c, _ = copy(command, BASE + '/runs/PG2584-v1/', 30)
    if c:
        raise ValueError('fixed audit execution transfer required')
    c, output = run('python3 -B ' + BASE + '/runs/PG2584-v1/audit.private.py', 120)
    (out / 'references.private.log').write_text(output)
    result = {'actualExit': c, 'source': SOURCE, 'operatorHead': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], text=True).strip(), 'auditJavaSha256': sha,
        'asmSha256': asm_sha, 'privateLogSha256': hashlib.sha256(output.encode()).hexdigest(),
        'coverageCredit': 0, 'unreachableAccepted': False, 'MainChanged': False,
        'vmActions0': True, 'reflectionSourceTestAuditPending': True, 'formalAccepted': False}
    if not c:
        result['methods'] = [line.strip() for line in output.splitlines() if line.startswith('METHOD ')]
        result['callers'] = [line.strip() for line in output.splitlines() if line.startswith('CALLER ')]
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    print(json.dumps({k: v for k, v in result.items() if k not in ['methods', 'callers']}))
    return c


if __name__ == '__main__':
    raise SystemExit(main())
