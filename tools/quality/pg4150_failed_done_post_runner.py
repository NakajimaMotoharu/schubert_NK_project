"""Freeze independent post before recovery; run once only after original recovery's actual0 receipt."""
import hashlib
import inspect
import json
import os
import stat
import sys
from pyflakes.api import check
import pg4148_failed_done_independent_post as source
from pg1446_current_cold_stage import W
import pg4106_failed_done_owned_inspect_runner as guard
import pg4058_original_read_profile as transport

ARTIFACT=W/'pg4150-failed-done-post-artifact-v1'
RECOVERY_RESULT=W/'pg4152-exact-failed-done-recover-v1/manifest.safe.json'


def main():
    if sys.argv[1:]not in (['freeze'],['run']):raise SystemExit('freeze or run; no service operations')
    os.umask(0o077)
    if sys.argv[1]=='freeze':
        ARTIFACT.mkdir(mode=0o700);raw=source.payload().encode()
        if check(raw.decode(),'<independent post>'):raise ValueError('complete static post first')
        p=ARTIFACT/'post.private.py'
        with p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
        p.chmod(0o400)
        value={'payloadSha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'stateChangingActions':0}
        (ARTIFACT/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return 0
    receipt=json.loads(RECOVERY_RESULT.read_bytes())
    if receipt['actualExit']!=0 or receipt['result']['mode']!='recover'or receipt['result']['newScopeNormalClose']is not True:
        raise ValueError('original recovered actual0 receipt first; never replay recovery')
    p=ARTIFACT/'post.private.py';m=guard.meta(p);raw=p.read_bytes();fixed=json.loads((ARTIFACT/'manifest.safe.json').read_bytes())
    if not(stat.S_ISREG(m[4])and m[2]==os.geteuid()and stat.S_IMODE(m[4])==0o400 and m[5]==1 and not os.listxattr(p)):
        raise ValueError('independent post envelope refused')
    if guard.meta(p)!=m or hashlib.sha256(raw).hexdigest()!=fixed['payloadSha256']or raw!=source.payload().encode():
        raise ValueError('independent post artifact changed')
    # Existing reader performs only M/A/RODB/metadata observation. It never stops an actor.
    ns={**vars(transport),'SLOT':source.SLOT,'payload':lambda unused:raw.decode(),
        'sys':type('PostArguments',(),{'argv':['independent_post','run']})}
    exec(compile(inspect.getsource(transport.main),'<frozen independent post transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
