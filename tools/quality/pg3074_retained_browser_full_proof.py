"""SSC276 full current original/runtime and exact live101/4FD/same-peer proof, signals0."""
import inspect
import json
import types
from pyflakes.api import check
import pg2964_retained_full_pair_proof as previous
import pg3040_current_runtime_retirement_post as current
from pg3070_retained_browser_readonly import host_owner
from pg1446_current_cold_stage import W

SLOT = 'pg3074-retained-browser-full-proof-v1'
FAILURE_SHA = 'e3f25b73a575626f9acbedc72d5ab9c18ba51e74325774f0377d7f75527aeb2d'


def bind(raw):
    for old, new in [('118988', '208849'), ('1642675', '2423591'), ('118986', '208847'), ('119019', '208880'), ('1642861', '2423775'), ('119017', '208878'), ('pg2950-current-cold-resume-tools-v1', 'pg3060-browser-resume-tools-v1'), ('pg2950_native_refs.py', 'pg3060_native_refs.py'), ('Pg2950FreshResumePreparation', 'Pg3060FreshResumePreparation'), ('pg2954-current-cold-resume-preparation-v1', 'pg3064-browser-resume-preparation-v1'), ('pg2964-retained-full-pair-proof-v1', SLOT), ('f176d954ada998d12fec8a7227f66882d208aebce430f107823c36eeb123910e', FAILURE_SHA)]:
        raw = raw.replace(old, new)
    return raw


def helpers():
    return bind(previous.helpers())


def body():
    raw = inspect.getsource(previous.body).replace('pg2940-current-resume-before-v1', 'pg3040-current-runtime-retirement-post-v1').replace('pg2890-network-owned-stop-tools-v1/pg2890_parent_receipt.py', 'pg3034-current-runtime-retirement-tools-v1/pg3034_parent_receipt.py')
    ns = {**previous.__dict__, 'current_post': current.payload, 'helpers': helpers}
    exec(compile(raw, '<current whole raw/metadata retained proof>', 'exec'), ns)
    return bind(ns['body']())


def tail():
    raw = bind(previous.TAIL)
    old = "require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').exists())"
    if raw.count(old) != 1:
        raise ValueError('one historical absent-parent guard to replace by actual immutable image')
    raw = raw.replace(old, "require(tree(pathlib.Path('/run/systemd/system'))==after['runtime'] and set(after['runtime'])=={'/run/systemd/system','/run/systemd/system/schubert-nk-morning-controller.service.d'})")
    return raw.replace("'runtimeDirectoryAbsent':True", "'runtimeOriginalParentUnchanged':True")


def payload():
    frozen = json.loads((W / 'pg3062-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit'] != 0:
        raise ValueError('actual latest frozen ABI required')
    raw = 'TOOL_HASHES=' + repr(frozen['fileHashes']) + '\n' + body() + tail()
    if check(raw, '<whole new retained pair proof>'):
        raise ValueError('complete current recovery proof namespace required')
    compile(raw, '<signals0 full original/retained-parent/pair proof>', 'exec')
    return raw


def main():
    fn = previous.main
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'payload': payload, 'host_owner': host_owner}, 'actual_current_retained_full_proof')()


if __name__ == '__main__':
    raise SystemExit(main())
