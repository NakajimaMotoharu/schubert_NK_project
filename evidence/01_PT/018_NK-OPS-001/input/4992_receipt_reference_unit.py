"""Run the one qualified ReceiptReference JUnit classes in a fresh owned slot."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import platform
import subprocess

ROOT = Path.cwd()
WORK = ROOT.parent / 'pgpt-runs/PG379'
EVIDENCE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence'
PREPARE = WORK / 'pg38246-receipt-reference-prepare-v1'
SLOT = WORK / 'pg38250-receipt-reference-unit-v1'
OUT = EVIDENCE / 'PG38250-receipt-reference-unit-v1'
JAVA = ROOT.parent / 'toolchain/jdk-25.0.4/bin/java'

def sha(path):
    return sha256(path.read_bytes()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def write(name, data):
    with (OUT / name).open('x') as stream:
        stream.write(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

prepare_path = EVIDENCE / 'PG38246-receipt-reference-prepare-v1/manifest.json'
admission_path = EVIDENCE / 'PG38244-receipt-reference-value-v1/admission.json'
prepare = json.loads(prepare_path.read_bytes())
admission = json.loads(admission_path.read_bytes())
assert admission['prepareSha256'] == sha(prepare_path)
assert admission['actualExit'] == admission['applicable'] == admission['unclassified'] == 0
source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
for name, digest in prepare['inputHashes'].items():
    assert sha(ROOT/name) == digest
    assert sha256(subprocess.check_output(['git', 'show', f'{source}:{name}'])).hexdigest() == digest
for name, digest in prepare['dependencies'].items():
    assert sha(Path(name)) == digest
for directory, key in [('component', 'physicalClassHashes'), ('test-classes', 'testClassHashes')]:
    path = PREPARE / directory
    assert {p.relative_to(path).as_posix(): sha(p) for p in path.rglob('*.class')} == prepare[key]
for name, digest in prepare['resourceCopies'].items():
    assert sha(PREPARE/'test-classes'/name.split('/src/test/resources/')[1]) == digest
assert prepare['expectedTests'] == 3 and len(prepare['selectedClasses']) == 1
SLOT.mkdir(mode=0o700)
OUT.mkdir()
for directory in ('xml', 'tmp'):
    (SLOT/directory).mkdir(mode=0o700)
agent = ROOT.parent/'toolchain/m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
class_path = ':'.join([str(PREPARE/'test-classes'), str(PREPARE/'component'), *prepare['dependencies']])
command = [str(JAVA), '-Dfile.encoding=UTF-8', '-Duser.timezone=Asia/Tokyo',
           '-Djava.io.tmpdir='+str(SLOT/'tmp'), '-Xlog:class+init=info:file='+str(SLOT/'class-init.log'),
           '-javaagent:'+str(agent)+'=destfile='+str(SLOT/'jacoco.exec')+',append=false,sessionid=PG38250-RECEIPT-REFERENCE-3',
           '-cp', class_path, 'org.junit.platform.console.ConsoleLauncher', 'execute',
           '--disable-banner', '--details=summary', '--fail-if-no-tests', '--reports-dir', str(SLOT/'xml')]
for fixture in prepare['selectedClasses']:
    command.extend(['--select-class', fixture])
write('begin.json', dict(source=source, run='PG38250-RECEIPT-REFERENCE-3', os=platform.platform(),
    branch='dev-foundation', startedAtUTC=now(), command=command, cwd=str(SLOT), javaSha256=sha(JAVA),
    jacocoAgentSha256=sha(agent), admissionSha256=sha(admission_path), expectedCases=prepare['expectedCases']))
with (OUT/'unit.stdout').open('xb') as stdout, (OUT/'unit.stderr').open('xb') as stderr:
    try:
        result = subprocess.run(command, cwd=SLOT, stdout=stdout, stderr=stderr, check=False, timeout=120)
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        exit_code = None
write('exit.json', dict(actualExit=exit_code, timedOut=exit_code is None, terminalAtUTC=now()))
print('PG38250 unit raw exit', exit_code)
raise SystemExit(exit_code if exit_code is not None else 124)
