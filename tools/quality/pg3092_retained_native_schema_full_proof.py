"""Exact latest retained pair plus full original/native16; missing-native diagnosis is not PASS."""
import types
import pg3074_retained_browser_full_proof as previous
from pg3088_retained_native_schema_readonly import host_owner

SLOT = 'pg3092-retained-native-schema-full-proof-v2'
FAILURE_SHA = '5d9d03870e0db0caf87240fd8e3b01207717253b761f9cf130aedfa24a82f1f8'


def bind(raw):
    for old, new in [('208849', '210904'), ('2423591', '2505343'), ('208847', '210902'), ('208880', '210935'), ('2423775', '2505531'), ('208878', '210933'), (previous.SLOT, SLOT), ('pg3060-browser-resume-tools-v1', 'pg3080-retained-parent-resume-tools-v1'), ('pg3060_native_refs.py', 'pg3080_native_refs.py'), ('Pg3060FreshResumePreparation', 'Pg3080FreshResumePreparation'), ('pg3064-browser-resume-preparation-v1', 'pg3084-retained-parent-resume-preparation-v1'), (previous.FAILURE_SHA, FAILURE_SHA)]:
        raw = raw.replace(old, new)
    return raw


def payload():
    raw = previous.payload()
    # Latest frozen source, not the previous failed3060 graph.
    import json
    from pg1446_current_cold_stage import W
    old = 'TOOL_HASHES=' + repr(json.loads((W / 'pg3062-frozen-v1.safe.json').read_bytes())['fileHashes'])
    if raw.count(old) != 1:
        raise ValueError('one exact old freeze header required')
    raw = raw.replace(old, 'TOOL_HASHES=' + repr(json.loads((W / 'pg3082-frozen-v1.safe.json').read_bytes())['fileHashes']))
    raw = bind(raw).replace("{'refs-prepare.private.log'}", "{'refs-prepare.private.log','before.private.json'}")
    marker = 'a=pair();require(a==pair());locks='
    extra = """missing_path=failed/'before.private.json';s=missing_path.lstat()
require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(missing_path))
missing_bytes=missing_path.read_bytes();missing=json.loads(missing_bytes)
require(set(missing)==set(after)-{'native'}and all(missing[k]==after[k]for k in missing)and missing_bytes==missing_path.read_bytes())
"""
    if raw.count(marker) != 1:
        raise ValueError('one current pair proof boundary required')
    raw = raw.replace(marker, extra + marker)
    compile(raw, '<current full preserved native despite old missing-field error>', 'exec')
    return raw


def main():
    payload()  # Complete generated closure before even creating a local new-only slot.
    fn = previous.previous.main
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'payload': payload, 'host_owner': host_owner}, 'new_native_schema_full_proof')()


if __name__ == '__main__':
    raise SystemExit(main())
