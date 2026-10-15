"""SSC274/276/277: exact fresh-qualified child then Java, durable once and queued gate."""
import inspect
import json
import types
import pg2966_retained_pair_owned_handoff as previous
import pg3074_retained_browser_full_proof as proof
from pg3070_retained_browser_readonly import host_owner
from pg1446_current_cold_stage import W

SLOT = 'pg3076-retained-browser-owned-handoff-v1'


def proof_sha():
    actual = json.loads((W / proof.SLOT / 'manifest.safe.json').read_bytes())
    if actual['actualExit'] != 0:
        raise ValueError('actual current full proof required before action')
    return actual['guest']['proofSha256']


def payload():
    raw = inspect.getsource(previous.payload)
    for old, new in [('119019', '208880'), ('1642861', '2423775'), ('118988', '208849'), ('1642675', '2423591'), ("expected['runtimeDirectoryAbsent']", "expected['runtimeOriginalParentUnchanged']")]:
        raw = raw.replace(old, new)
    old = "not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').exists()and {p.name for p in failed.iterdir()}=={'refs-prepare.private.log'}"
    if raw.count(old) != 1:
        raise ValueError('one historical runtime shape constraint required')
    raw = raw.replace(old, "tree(pathlib.Path('/run/systemd/system'))==after['runtime'] and {p.name for p in failed.iterdir()}=={'refs-prepare.private.log'}")
    ns = {**previous.__dict__, 'proof': proof, 'SLOT': SLOT, 'PROOF_SHA': proof_sha()}
    exec(compile(raw, '<exact current only two owned terms>', 'exec'), ns)
    return ns['payload']()


def main():
    fn = previous.main
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'proof': proof, 'SLOT': SLOT, 'PROOF_SHA': proof_sha(), 'payload': payload, 'host_owner': host_owner}, 'current_browser_owned_handoff')()


if __name__ == '__main__':
    raise SystemExit(main())
