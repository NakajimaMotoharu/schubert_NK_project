"""Separate new-only fixed tool stage and owned unused placement; no publication/start."""
import hashlib
import datetime
import json
import sys
import types

import pg2660_operation_unused_dispatch as old
import pg3434_current_outbox_candidate_sources as role
import pg3436_current_outbox_candidate_compile as compiler
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate

TARGET = compiler.TARGET
GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS


def bind(raw):
    for before, after in [(role.old.TOOLS, role.TOOLS), (role.old.SAVE, role.SAVE),
                          (role.old.ARCHIVE, role.ARCHIVE), (role.old.REMOTE, role.REMOTE),
                          ('pg2660-fixed-stage-v1', 'pg3438-fixed-stage-v1')]:
        raw = raw.replace(before, after)
    raw = compiler.bind(raw).replace('pg2660', 'pg3438').replace('PG2660', 'PG3438')
    raw = raw.replace('0.1.0-PG2512', '0.1.0-PG2802')
    raw = raw.replace(role.old.BOOT, role.BOOT).replace('PG2134_IMMUTABLE_STAGE', 'PG3438_IMMUTABLE_STAGE_V2')
    return raw


STAGE = bind(old.STAGE)


def source():
    raw = bind(old.source())
    if raw.count('2f7ca23be804567a5d9a61636cf4c1d4ec96fcd0') != 1:
        raise ValueError('exact complete source input boundary required')
    raw = raw.replace('2f7ca23be804567a5d9a61636cf4c1d4ec96fcd0', role.SOURCE)
    raw = raw.replace("pg3438-stage-v1.exit", "pg3438-stage-v2.exit")
    compile(raw, '<current a9/new4856 distinct new-only stage/place>', 'exec')
    return raw


def before_record():
    path = W / 'pg3430-current-a9-readonly-before-v1/manifest.safe.json'
    proof = json.loads(path.read_bytes())
    view = json.loads((W / 'pg3432-current-a9-before-view-v2/manifest.safe.json').read_bytes())
    if (view['freshEqualityWitnessManifestSha256'] != hashlib.sha256(path.read_bytes()).hexdigest()
            or proof['actualExit'] != 0 or proof['productionSource'] != role.CURRENT
            or view['productionSource'] != role.CURRENT or not view['dataOnlyNotRuntimeAuthority']):
        raise ValueError('same authenticated data-only view and actual current Root completion proof')
    return {**view, 'genuineCompletion': proof['genuineCompletion']}


def runtime_namespace(candidate, before):
    if before.get('runtimeAlreadyRetired') is not True or before.get('dataOnlyNotRuntimeAuthority') is not True:
        raise ValueError('already-retired current data, not recovery authority')
    engine = old.previous.engine
    fn = types.FunctionType(engine.runtime_namespace.__code__,
                            {**engine.__dict__, 'CURRENT': role.CURRENT, 'BEFORE': role.BEFORE,
                             'TARGET': TARGET, 'GUEST': GUEST, 'REMOTE': role.REMOTE,
                             'STAGE': STAGE, 'production': role.production, 'sources': role.sources})
    return {**fn(candidate, before), '__file__': __file__}


def stage_resume():
    """Only the root tool extraction not reached by the proven boot refusal.

    Authenticate and reuse original uploads; never replay SCP/mkdir/stage-v1.
    The original failed reservation/exit remains immutable.
    """
    import os
    import subprocess
    from pathlib import Path

    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('fixed clean recovery operator required')
    if subprocess.check_output(['git', 'diff', role.SOURCE, 'HEAD', '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']):
        raise ValueError('exact signed candidate source required')
    first = json.loads((W / 'pg3438-stage-v1.safe.json').read_bytes())
    first_log = W / 'pg3438-stage-v1.private.log'
    if (first['actualExit'] != 1 or first['action'] != 'stage'
            or hashlib.sha256(first_log.read_bytes()).hexdigest() != first['privateLogSha256']
            or 'line 20' not in first_log.read_text() or 'AssertionError' not in first_log.read_text()
            or (W / 'pg3438-stage-v1.exit').read_bytes() != b'1\n'):
        raise ValueError('exact original pre-write boot refusal required; unknown partial state not replayed')
    frozen = json.loads((W / 'pg3436-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit'] != 0 or frozen['candidateSource'] != role.SOURCE or frozen['candidateManifestSha256'] != role.BOM:
        raise ValueError('same actual frozen ABI and signed candidate')
    for name, digest in frozen['fileHashes'].items():
        if hashlib.sha256((TARGET / name).read_bytes()).hexdigest() != digest:
            raise ValueError('same frozen tool inputs required')
    local = [(P / role.ARCHIVE, role.REMOTE + '/' + role.ARCHIVE),
             (P / 'pg3420-manifest-v1.sig', role.REMOTE + '/pg3420-manifest-v1.sig'),
             (TARGET / 'bundle.safe.json', role.REMOTE + '/bundle.safe.json'),
             (P / (role.TOOLS + '.tar'), '/home/ubuntu/pg3438-fixed-stage-v1/' + role.TOOLS + '.tar')]
    inputs = {remote: {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'size': path.stat().st_size} for path, remote in local}
    bundle = json.loads((TARGET / 'bundle.safe.json').read_bytes())
    if (inputs[local[0][1]]['sha256'] != bundle['archiveSha256']
            or inputs[local[1][1]]['sha256'] != bundle['signatureSha256']):
        raise ValueError('original signed bundle unchanged')
    verify = """import pathlib,hashlib,os,stat
for name,expected in INPUTS.items():
 p=pathlib.Path(name);s=p.lstat()
 assert p.resolve()==p and stat.S_ISREG(s.st_mode)and s.st_nlink==1 and s.st_size==expected['size']and not(s.st_mode&0o022)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==expected['sha256']
"""
    payload = ('INPUTS=' + repr(inputs) + '\nDIGEST=' + repr(inputs[local[3][1]]['sha256'])
               + '\nFILES=' + repr(frozen['fileHashes']) + '\n' + verify + '\n' + STAGE)
    base = W / 'pg3438-stage-v2'
    if any(Path(str(base) + suffix).exists() for suffix in ['.begin.safe.json', '.private.log', '.exit', '.safe.json', '.payload.private.py']):
        raise ValueError('stage-resume reservation already used; recover original result')
    os.umask(0o077)
    operator = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    begin = {'action': 'stage-resume', 'state': 'RESERVED_NOT_ACCEPTED', 'startedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'operatorSource': operator, 'candidateSource': role.SOURCE, 'installedSource': role.CURRENT,
             'originalStageV1Sha256': hashlib.sha256((W / 'pg3438-stage-v1.safe.json').read_bytes()).hexdigest(),
             'originalUploadsReauthenticatedAndReused': True, 'scpReissued': False, 'businessReissued': False, 'formalAccepted': False}
    with Path(str(base) + '.begin.safe.json').open('x') as f: json.dump(begin, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    Path(str(base) + '.payload.private.py').write_text(payload)
    with Path(str(base) + '.private.log').open('xb') as log:
        actual = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=payload.encode(), stdout=log, stderr=log, timeout=120)
        log.flush(); os.fsync(log.fileno())
    with Path(str(base) + '.exit').open('x') as f: f.write(str(actual.returncode) + '\n'); f.flush(); os.fsync(f.fileno())
    completed = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    result = {**begin, 'actualExit': actual.returncode, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'privateLogSha256': hashlib.sha256(Path(str(base) + '.private.log').read_bytes()).hexdigest(),
              'payloadSha256': hashlib.sha256(payload.encode()).hexdigest(), 'operatorSourceUnchanged': operator == completed,
              'sourceQualified': actual.returncode == 0 and operator == completed, 'rootToolStageOnly': True,
              'currentApprovalEpochChanged': False, 'startsStopsReloadsSqlWrites0': True}
    with Path(str(base) + '.safe.json').open('x') as f: json.dump(result, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    print(json.dumps(result)); return actual.returncode


def main():
    if sys.argv[1:] == ['stage-resume']:
        role.qualify()
        with management_gate(P / 'current-management-critical.lock'):
            return stage_resume()
    if sys.argv[1:] not in (['stage'], ['place']):
        raise ValueError('explicit distinct stage/place only')
    role.qualify()
    candidate = json.loads((W / 'pg3420-candidate-build-v1.safe.json').read_bytes())
    namespace = runtime_namespace(candidate, before_record())
    exec(compile(source(), '<new unused current/candidate dispatcher>', 'exec'), namespace)
    with management_gate(P / 'current-management-critical.lock'):
        return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
