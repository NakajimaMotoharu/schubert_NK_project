"""Independent full original/native/resources post; old3064 UNKNOWN stays UNKNOWN."""
import inspect
import json
import types
import pg2968_recovered_pair_full_post as previous
import pg3040_current_runtime_retirement_post as current
from pg3074_retained_browser_full_proof import FAILURE_SHA
from pg1446_current_cold_stage import W

SLOT = 'pg3078-recovered-browser-full-post-v1'


def payload(seals):
    raw = inspect.getsource(previous.payload)
    raw = raw.replace('PG2940-current-resume-before-v1', 'PG3040-current-runtime-retirement-post-v1').replace('PG2968-recovered-pair-full-post-v1', 'PG3078-recovered-browser-full-post-v1')
    for old, new in [('pg2966-retained-pair-owned-handoff-v1', 'pg3076-retained-browser-owned-handoff-v1'), ('pg2954-current-cold-resume-preparation-v1', 'pg3064-browser-resume-preparation-v1'), ('118988', '208849'), ('119019', '208880'), ('f176d954ada998d12fec8a7227f66882d208aebce430f107823c36eeb123910e', FAILURE_SHA)]:
        raw = raw.replace(old, new)
    ns = {**previous.__dict__, 'previous': current, 'SLOT': SLOT}
    exec(compile(raw, '<current whole recovered all-original post>', 'exec'), ns)
    return ns['payload'](seals)


def main():
    receipt = json.loads((W / 'pg3076-retained-browser-owned-handoff-v1/manifest.safe.json').read_bytes())
    if not (receipt['actualExit'] == 0 and receipt['gateHandoffComplete'] and receipt['oldCloseUnknown']):
        raise ValueError('actual current exact owned recovery required')
    fn = current.namespace()['main']
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'payload': payload}, 'current_browser_recovered_full_post')()


if __name__ == '__main__':
    raise SystemExit(main())
