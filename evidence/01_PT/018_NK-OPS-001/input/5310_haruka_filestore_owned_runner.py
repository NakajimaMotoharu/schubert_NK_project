"""Run one ordinary synthetic GateCli preflight in a newly owned haruka directory."""
from pathlib import Path
from datetime import datetime, timezone
import base64
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from xml.etree import ElementTree as ET

ROOT = Path('/home/mini/schubert-nk-pgpt/validation-work')
TOOL = Path('/opt/schubert-nk-test-tools/jdk-25.0.4/bin')
RUN = 'PG40160-p020-haruka-real-filestore-v1'
MIN_BYTES = 20 * 1024**3
BASE = 'dev.codex.schubert.characterization.GateCli'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def send(tag, value):
    print(tag + json.dumps(value, separators=(',', ':')), flush=True)


def boot_id():
    return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def host_proof(spec):
    assert Path('/etc/hostname').read_text().strip() == 'haruka'
    assert ROOT.resolve() == ROOT
    props = ROOT.stat()
    assert ROOT.is_dir() and props.st_uid == os.getuid() == 1000
    assert props.st_mode & 0o777 == 0o700 and os.access(ROOT, os.W_OK | os.X_OK)
    assert not os.path.lexists(ROOT / RUN)
    assert shutil.disk_usage(ROOT).free >= MIN_BYTES
    live = []
    for proc in Path('/proc').iterdir():
        if proc.name.isdecimal():
            try:
                if proc.stat().st_uid == os.getuid() and Path(os.readlink(proc / 'cwd')).is_relative_to(ROOT):
                    live.append(int(proc.name))
            except OSError:
                continue
    assert not live
    for name in ('java', 'javac'):
        path = TOOL / name
        assert os.access(path, os.R_OK | os.X_OK) and sha(path.read_bytes()) == spec[name]
    return dict(host='haruka', boot=boot_id(), uid=os.getuid(), workspaceMode='0700',
                workspace=str(ROOT), device=props.st_dev, freeBytes=shutil.disk_usage(ROOT).free,
                runAbsent=True, activeOwnedWorkspaceJobs=0, observedAtUTC=utc())


def read_capsule(spec):
    encoded = bytearray()
    while True:
        line = sys.stdin.buffer.readline(2000)
        assert line.endswith(b'\n')
        if line == b'PAYLOAD-END\n':
            break
        encoded.extend(line.strip())
        assert len(encoded) <= 10 * 1024**2
    capsule = base64.b64decode(encoded, validate=True)
    assert len(capsule) == spec['size'] and sha(capsule) == spec['capsuleSha256']
    files = {}
    with tarfile.open(fileobj=io.BytesIO(capsule), mode='r:') as tar:
        entries = tar.getmembers()
        assert len(entries) == len(spec['files']) and {entry.name for entry in entries} == spec['files'].keys()
        for entry in entries:
            assert entry.isfile() and not Path(entry.name).is_absolute() and '..' not in Path(entry.name).parts
            data = tar.extractfile(entry).read()
            assert sha(data) == spec['files'][entry.name]
            files[entry.name] = data
    return files


def command(argv, cwd, expected=0):
    done = subprocess.run(list(map(str, argv)), cwd=cwd, capture_output=True, timeout=35,
                          env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}, check=False)
    return dict(actualExit=done.returncode, expectedExit=expected, stdoutSha256=sha(done.stdout),
                stderrSha256=sha(done.stderr), command=list(map(str, argv)))


def method_counters(path):
    doc = ET.parse(path).getroot()
    cls, = (row for row in doc.iter('class') if row.get('name') == BASE.replace('.', '/'))
    selectors = {
        ('main', '([Ljava/lang/String;)V'),
        ('preflight', '(Ljava/nio/file/Path;Ljava/nio/file/Path;)V'),
    }
    return {m.get('name'): {c.get('type'): dict(covered=int(c.get('covered')), missed=int(c.get('missed')))
                            for c in m.findall('counter')}
            for m in cls.findall('method') if (m.get('name'), m.get('desc')) in selectors}


def run(spec):
    stage = 'precheck'
    allocated = False
    child = {}
    try:
        before = host_proof(spec)
        send('HARUKA_READY ', before)
        stage = 'capsule'
        files = read_capsule(spec)
        assert boot_id() == before['boot'] and ROOT.stat().st_dev == before['device']
        assert shutil.disk_usage(ROOT).free >= MIN_BYTES
        os.umask(0o077)
        area = ROOT / RUN
        area.mkdir(mode=0o700)
        allocated = True
        for name, raw in files.items():
            path = area / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as f:
                f.write(raw)
        stage = 'compile'
        physical = area / 'classes'
        physical.mkdir()
        sdk = sorted((area / 'sdk').glob('*.jar'))
        compile_sdk = [p for p in sdk if not p.name.startswith('org.jacoco.')]
        sources = sorted((area / 'program/characterization/src/main/java').rglob('*.java'))
        assert len(sources) == 6 and len(compile_sdk) == 5 and len(sdk) == 7
        cp = os.pathsep.join(map(str, compile_sdk))
        child['javac'] = command([TOOL/'javac', '--release', '25', '-g', '-Xlint:all', '-Werror',
                                   '-proc:none', '-cp', cp, '-d', physical, *sources], area)
        assert child['javac']['actualExit'] == 0
        actual_physical = {p.relative_to(physical).as_posix(): sha(p.read_bytes()) for p in physical.rglob('*.class')}
        assert actual_physical == spec['classHashes'] and len(actual_physical) == 17
        stage = 'fixtures'
        for name in ('current/program/app/src', 'assets', 'pg-data', 'diagnostics', 'runtime'):
            (area / name).mkdir(parents=True)
        for name in ('non-executable-current.jar', 'test-users.txt', 'non-executable-pgctl', 'non-executable-caddy'):
            p = area / name
            p.write_text('OWNED PUBLIC TEST FIXTURE ONLY\n')
            assert p.stat().st_mode & 0o777 == 0o600
        args = dict(projectRoot=area, currentRoot=area/'current', currentJar=area/'non-executable-current.jar',
                    assetRoot=area/'assets', usersFile=area/'test-users.txt', javaExecutable=TOOL/'java',
                    caddyExecutable=area/'non-executable-caddy', runtimeRoot=area/'runtime',
                    pgCtl=area/'non-executable-pgctl', pgData=area/'pg-data', pgLog=area/'diagnostics/pg.log',
                    pgSocket=area/'runtime/pgsocket', dbUrl='jdbc:postgresql://127.0.0.1:15432/synthetic',
                    appPort=18081, proxyPort=18082)
        coverage_exec = area / 'file-store.exec'
        agent = area / 'sdk/org.jacoco.agent-0.8.15-runtime.jar'
        session = 'PG40160-HARUKA-OWNED-FILESTORE-ONLY'
        answer = area / 'preflight.json'
        stage = 'preflight'
        pre = shutil.disk_usage(area/'runtime').free
        child['unit'] = command([TOOL/'java', '-Xmx512m', *[f'-Dchr.{k}={v}' for k,v in args.items()],
                                 f'-javaagent:{agent}=destfile={coverage_exec},sessionid={session},append=false',
                                 '-cp', str(physical)+os.pathsep+cp, BASE, 'preflight', answer], area)
        post = shutil.disk_usage(area/'runtime').free
        assert child['unit']['actualExit'] == 0
        result = json.loads(answer.read_bytes())
        assert result['status'] == 'PASS' and result['failures'] == []
        assert type(result['freeBytes']) is int and min(pre, post, result['freeBytes']) >= MIN_BYTES
        assert result['credentialPermission'] == '0600' and result['hostAllowlist'] == ['localhost', '127.0.0.1']
        assert result['runtimeRoot'] == str(area/'runtime') and result['projectRoot'] == str(area)
        assert boot_id() == before['boot'] and (area/'runtime').stat().st_dev == before['device']
        stage = 'coverage'
        cli = area / 'sdk/org.jacoco.cli-0.8.15-nodeps.jar'
        report = area / 'coverage.xml'
        child['report'] = command([TOOL/'java', '-jar', cli, 'report', coverage_exec,
                                   '--classfiles', physical, '--xml', report], area)
        assert child['report']['actualExit'] == 0
        counters = method_counters(report)
        assert set(counters) == {'main', 'preflight'}
        assert counters['preflight']['METHOD']['covered'] == 1
        payloads = {}
        for path in (answer, coverage_exec, report):
            raw = path.read_bytes()
            assert len(raw) <= 1000000
            payloads[path.name] = dict(sha256=sha(raw), data=base64.b64encode(raw).decode())
        send('HARUKA_TERMINAL ', dict(actualExit=0, allocatedRun=True, boot=before['boot'], ownerUid=os.getuid(),
                                      workspace=str(area), invocationPid=os.getpid(), terminalAtUTC=utc(),
                                      session=session, fileStoreIndependentBytes=dict(before=pre, after=post),
                                      methods=counters, stages=child, physical=actual_physical,
                                      payloads=payloads, productTests=0, realBackendActions=0))
    except (AssertionError, OSError, ValueError, KeyError, subprocess.SubprocessError) as failure:
        send('HARUKA_TERMINAL ', dict(actualExit=1, stage=stage, errorType=type(failure).__name__, allocatedRun=allocated,
                                      stages=child, terminalAtUTC=utc()))
        raise SystemExit(1)
