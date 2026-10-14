"""SSC274/276/277 exact current pair: queued gate, durable once TERM, no restart."""
import datetime
import hashlib
import inspect
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W, P, SSH
from pg1724_retained_host_gate import queued_gate
from pg2960_retained_resume_readonly import host_owner
import pg2964_retained_full_pair_proof as proof
from pg1667_unused_pair_once_handoff import BODY as proven_body
from pg1665_unused_pair_contract import fresh_parent, parent_after_ref
from pg782_owned_handoff import terminate
from pg1680_proc_reap_contract import confirmed_absence

SLOT = 'pg2966-retained-pair-owned-handoff-v1'
PROOF_SHA = 'c1170b22495c28a114640f2f1153c92c9fa673431b0fc35e4e0039d0ca9cb510'


def payload():
    raw = proof.payload()
    raw = raw[:raw.index('a=pair();require(a==pair());locks=')]
    body = proven_body
    for a, b in [('pg1664-current-unused-pair-proof-v1', proof.SLOT), ('pg1667-unused-pair-owned-handoff-v1', SLOT), ('291242', '119019'), ('5962938', '1642861'), ('291213', '118988'), ('5962776', '1642675'), ('0.1.0-PG1544', '0.1.0-PG2802')]:
        body = body.replace(a, b)
    body = body.replace("expected['candidateNotPlaced']", "expected['runtimeDirectoryAbsent']")
    old = "  require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists()and not(base/'pg1638-manifest.sig').exists())"
    new = "  require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').exists()and {p.name for p in failed.iterdir()}=={'refs-prepare.private.log'})"
    if body.count(old) != 1:
        raise ValueError('one obsolete unused-candidate assertion to bind')
    body = body.replace(old, new)
    for a, b in [("['29', '32']", "['31', '90']"), ("{'29', '32'}", "{'31', '90'}"), ("['29']", "['31']"), ("['32']", "['90']")]:
        body = body.replace(a, b)
    guard = inspect.getsource(fresh_parent)
    for a, b in [("['29', '32']", "['31', '90']"), ("{'29', '32'}", "{'31', '90'}"), ("['29']", "['31']"), ("['32']", "['90']")]:
        guard = guard.replace(a, b)
    raw = 'import errno\nPROOF_SHA=' + repr(PROOF_SHA) + '\n' + guard + '\n' + inspect.getsource(parent_after_ref) + '\n' + inspect.getsource(confirmed_absence) + '\n' + inspect.getsource(terminate) + '\n' + raw + body
    if check(raw, '<current exact pair handoff>'):
        raise ValueError('complete owned handoff namespace required')
    compile(raw, '<current exact pair handoff>', 'exec')
    return raw


def main():
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean fixed operator required')
    for path in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md', 'documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md', 'documents/300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md', 'documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md']:
        text = subprocess.check_output(['git', 'show', 'origin/main:' + path], text=True)
        if 'SSC277' not in text and 'SSC-277' not in text:
            raise ValueError('published current recovery design required')
    old = json.loads((W / proof.SLOT / 'manifest.safe.json').read_bytes())
    if old['actualExit'] != 0 or old['guest']['proofSha256'] != PROOF_SHA:
        raise ValueError('current full pair proof required')
    os.umask(0o077)
    out = W / SLOT
    out.mkdir(mode=0o700)
    raw = payload().encode()
    (out / 'payload.private.py').write_bytes(raw)
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    completed = False
    with queued_gate(P / 'current-management-critical.lock', validate_owner=host_owner, require_completion=lambda: completed) as acquired:
        r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw, capture_output=True, timeout=180)
        (out / 'stderr.private.log').write_bytes(r.stderr)
        (out / 'stages.private.jsonl').write_bytes(r.stdout)
        completed = r.returncode == 0
        gate_ok = acquired.wait(30) if completed else False
        value = {'actualExit': r.returncode, 'payloadSha256': hashlib.sha256(raw).hexdigest(), 'startUTC': start, 'endUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'oldCloseUnknown': True, 'criticalGateQueuedWithoutForceUnlock': True, 'gateHandoffComplete': gate_ok, 'formalAccepted': False, 'stages': [json.loads(l) for l in r.stdout.splitlines() if l.startswith(b'{')]}
        with (out / 'manifest.safe.json').open('x') as f:
            json.dump(value, f, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        print(json.dumps(value), flush=True)
        if completed and not gate_ok:
            raise ValueError('old wrapper gate release not proven')
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
