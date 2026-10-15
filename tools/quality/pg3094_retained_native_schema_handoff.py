"""Exact210935 then210904 owned handoff after current full native16/original proof."""
import inspect
import json
import types
import pg3076_retained_browser_owned_handoff as template
import pg3092_retained_native_schema_full_proof as proof
from pg3088_retained_native_schema_readonly import host_owner
from pg1446_current_cold_stage import W

SLOT = 'pg3094-retained-native-schema-owned-handoff-v1'


def proof_sha():
    actual = json.loads((W / proof.SLOT / 'manifest.safe.json').read_bytes())
    if actual['actualExit'] != 0:
        raise ValueError('actual current c8d4 full proof required')
    return actual['guest']['proofSha256']


def payload():
    raw = inspect.getsource(template.payload)
    for old, new in [('208849', '210904'), ('2423591', '2505343'), ('208880', '210935'), ('2423775', '2505531')]:
        raw = raw.replace(old, new)
    ns = {**template.__dict__, 'proof': proof, 'proof_sha': proof_sha, 'SLOT': SLOT}
    exec(compile(raw, '<latest exact two actor handoff>', 'exec'), ns)
    return ns['payload']().replace("{'refs-prepare.private.log'}", "{'refs-prepare.private.log','before.private.json'}")


def main():
    fn = template.main
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'proof': proof, 'proof_sha': proof_sha, 'SLOT': SLOT, 'payload': payload, 'host_owner': host_owner}, 'native_schema_current_owned_handoff')()


if __name__ == '__main__':
    raise SystemExit(main())
