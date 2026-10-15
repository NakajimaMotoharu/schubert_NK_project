"""Independent complete post after exact latest pair handoff; no old UNKNOWN normalization."""
import inspect
import json
import types
import pg3078_recovered_browser_post as template
import pg3040_current_runtime_retirement_post as current
from pg3092_retained_native_schema_full_proof import FAILURE_SHA
from pg1446_current_cold_stage import W

SLOT = 'pg3096-recovered-native-schema-full-post-v1'


def payload(seals):
    raw = inspect.getsource(template.payload)
    for old, new in [('pg3076-retained-browser-owned-handoff-v1', 'pg3094-retained-native-schema-owned-handoff-v1'), ('pg3064-browser-resume-preparation-v1', 'pg3084-retained-parent-resume-preparation-v1'), ('208849', '210904'), ('208880', '210935'), ('PG3078-recovered-browser-full-post-v1', 'PG3096-recovered-native-schema-full-post-v1')]:
        raw = raw.replace(old, new)
    ns = {**template.__dict__, 'SLOT': SLOT, 'FAILURE_SHA': FAILURE_SHA}
    exec(compile(raw, '<latest complete native-schema recovered post>', 'exec'), ns)
    return ns['payload'](seals).replace("{'refs-prepare.private.log'}", "{'refs-prepare.private.log','before.private.json'}")


def main():
    receipt = json.loads((W / 'pg3094-retained-native-schema-owned-handoff-v1/manifest.safe.json').read_bytes())
    if not (receipt['actualExit'] == 0 and receipt['gateHandoffComplete'] and receipt['oldCloseUnknown']):
        raise ValueError('actual latest exact recovery required')
    fn = current.namespace()['main']
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'payload': payload}, 'current_native_schema_recovered_post')()


if __name__ == '__main__':
    raise SystemExit(main())
