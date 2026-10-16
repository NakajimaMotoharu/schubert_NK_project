"""SSC294 one-shot remaining-only observer. No timeout kill or old action replay."""
import hashlib
import inspect
import json
import os
import select
import shlex
import subprocess
import sys
import pg4188_exact_partial_recover as transport
import pg4382_half_handoff_stage as stage
import pg4368_pool_bound_recover as fixed_entry
from pg1446_current_cold_stage import W, P, SSH
from pg1724_retained_host_gate import queued_gate
from pg4152_exact_failed_done_recover import process, durable
from lan_server import run
import pg3428_vm_candidate_preflight_readonly as identity

OUT = W / 'pg4384-half-handoff-recover-v1'
DESIGN_MAIN = 'd6c8b23fdcec49e6cc086a0dd435a895b2bf2ce9'


def completed(result):
    def demand(value, expected):
        if type(value) is not dict or any(type(value.get(k)) is not type(v) or value[k] != v for k, v in expected.items()):
            raise ValueError('complete exact same-source remaining-only terminal required')
    source = '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e'
    base = {'actualExit': 0, 'source': source, 'BOM': '0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab',
            'boot': '79a3260a-e16d-42bf-942a-b914ed144c28', 'formalAccepted': False}
    demand(result, {**base, 'mode': 'recover', 'newTenRefsNormalClose': True, 'signalsIssued': 2,
                    'javaSignalsIssued': 0, 'caddyStopsReissued': 0, 'oldScopesNormal': False})
    demand(result.get('partialInspect'), {**base, 'mode': 'inspect', 'newScopeNormalClose': True})
    demand(result.get('partialRecover'), {**base, 'mode': 'recover', 'newScopeNormalClose': True,
             'newStopCount': 5, 'caddyPriorStopAuthenticated': True, 'original58917Normal': False,
             'recoverySixNormal': True, 'canonicalEpochRevoked': True, 'all37StartupEntriesPreserved': True})
    # The fixed independent post asserts this boot inside its immutable payload;
    # its published receipt does not expose a boot field. Do not invent one.
    demand(result.get('independentPost'), {**{k: v for k, v in base.items() if k != 'boot'}, 'newMARDDBTenRefNormalClose': True,
             'independentFailedDoneRecoveryPost': True, 'oldParentNormal': False, 'parent143StillFailed': True,
             'all24OriginalBackupNativeUnitConfigUnchanged': True, 'signalStartStopReloadDbWrites': 0})
    return result


def bootstrap(hashes):
    ns = {**vars(transport), 'GUEST': stage.GUEST}
    exec(compile(inspect.getsource(transport.bootstrap), '<single half-handoff staged envelope>', 'exec'), ns)
    return ns['bootstrap']('keeper.py', hashes)


def main():
    if sys.argv[1:] != ['recover'] or DESIGN_MAIN == 'PENDING_SSC294_MAIN':
        raise ValueError('one recovery only after final design-only publication')
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean fixed operator required')
    if subprocess.check_output(['git', 'diff', '--name-only', '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e', 'HEAD', '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']):
        raise ValueError('unchanged current whole-source before remaining-only recovery')
    subprocess.run(['git', 'merge-base', '--is-ancestor', DESIGN_MAIN, 'origin/main'], check=True)
    for name in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md',
                 'documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md']:
        if subprocess.check_output(['git', 'show', 'origin/main:' + name]) != subprocess.check_output(['git', 'show', DESIGN_MAIN + ':' + name]):
            raise ValueError('exact published remaining-only design required')
    hashes = {name: hashlib.sha256(raw.encode()).hexdigest() for name, raw in stage.files().items()}
    staged = json.loads((W / (stage.SLOT + '-stage') / 'manifest.safe.json').read_bytes())
    proof = json.loads((W / (stage.SLOT + '-proof') / 'manifest.safe.json').read_bytes())
    if staged['actualExit'] != 0 or staged['result']['files'] != hashes or proof['actualExit'] != 0 or proof['result']['signalsIssued'] != 0 or proof['result']['newTenRefsNormalClose'] is not True:
        raise ValueError('same artifact no-action complete proof required')
    if process(20445) != {'pid': 20445, 'ticks': 104194, 'argvSha256': 'fd6ff71b025aa4b485f64f9dd2289f9072ac6f78d9fc6a9c44912adf8bad097b'}:
        raise ValueError('fresh current exact forward required')
    code, text = run(identity.HOST, timeout=30)
    if code != 0 or json.loads(text)['boot'] != 'c7964823-c628-4ef2-99b5-07b0f0b62bba':
        raise ValueError('fresh same host/VM identity required')
    os.umask(0o077); OUT.mkdir(mode=0o700)
    durable(OUT / 'start.safe.json', {'owner': process(os.getpid()), 'source': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
                                    'files': hashes, 'designMain': DESIGN_MAIN, 'replayAllowed': False})
    with queued_gate(P / 'current-management-critical.lock', validate_owner=stage.owner) as acquired:
        with (OUT / 'stderr.private.log').open('xb') as error:
            args = SSH + [shlex.join(['sudo', '-n', 'python3', '-B', '-c', bootstrap(hashes), 'recover'])]
            child = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=error, text=True, bufsize=1)
            durable(OUT / 'ssh.private.json', process(child.pid))
            def frame(prefix):
                poll = select.poll(); poll.register(child.stdout.fileno(), select.POLLIN)
                if not poll.poll(240000): raise ValueError('original result missing; preserve without replay')
                line = child.stdout.readline(1001)
                if not line.endswith('\n') or not line.startswith(prefix): raise ValueError('unknown original phase; preserve child/metadata')
                with (OUT / 'stages.safe.log').open('a') as log: log.write(line); log.flush(); os.fsync(log.fileno())
            def ack(): child.stdin.write('CONTINUE\n'); child.stdin.flush()
            frame('SSC294_OWNERS_READY '); stage.owner(P / 'current-management-critical.lock'); ack()
            frame('SSC294_OLD_PYTHON_GONE originalTransportRequired=true')
            if not acquired.wait(30): raise ValueError('original gate natural release required')
            original = fixed_entry.original_receipt(json.loads((W / 'pg4316-current-failed-dispatch-v1-recover/manifest.safe.json').read_bytes()))
            durable(OUT / 'original4328-result.safe.json', original); ack()
            frame('SSC294_OLD_METADATA_GONE transportUnknownPreserved=true')
            durable(OUT / 'old-retainer-transport.safe.json', {'original4368ActualExit': 1, 'retainerSshActualExit': None,
                                                             'oldCloseNormal': False, 'reason': 'original observer already exited; guest terminal independently proved'})
            ack()
            tail = child.communicate()[0]; error.flush(); os.fsync(error.fileno())
        with (OUT / 'tail.private.log').open('x') as log: log.write(tail)
        value = {'actualExit': child.returncode, 'source': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
                 'original4328ActualExit': original['actualExit'], 'original4368ActualExit': 1,
                 'oldScopesNormal': False, 'formalAccepted': False}
        if child.returncode == 0:
            result = completed(json.loads(tail.splitlines()[-1]))
            value['result'] = result
        durable(OUT / 'manifest.safe.json', value); print(json.dumps(value)); return child.returncode


if __name__ == '__main__':
    raise SystemExit(main())
