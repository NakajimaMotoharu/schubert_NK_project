"""Fresh full live ownership/source/seal immediately before one owned stop."""
import inspect
import pg1327_published_completed_capture_v2 as previous
from pg1328_published_owned_stop_sources import BEFORE,GUEST_BEFORE


def payload():
    code=previous.payload().replace('published-completed-capture-v2','published-stop-preflight-v1')
    marker='current=capture();require(current==capture());SAVE.mkdir(mode=0o700)'
    if code.count(marker)!=1:raise ValueError('one full preflight seal join required')
    join='sealed_current=pathlib.Path('+repr(GUEST_BEFORE)+').read_bytes();require(hashlib.sha256(sealed_current).hexdigest()=='+repr(BEFORE)+');require(current==json.loads(sealed_current))'
    code=code.replace(marker,'current=capture();require(current==capture());'+join+';SAVE.mkdir(mode=0o700)')
    compile(code,'<actual current full preflight seal>','exec');return code


def main():
    env=dict(previous.previous.transport.__dict__,payload=payload)
    code=inspect.getsource(previous.previous.transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1330-published-stop-preflight-v1')
    exec(compile(code,'<new-only current four owner preflight>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
