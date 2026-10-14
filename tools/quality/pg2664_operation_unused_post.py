"""Independent new unused placement post; no reissue of stage/place."""
import ast
import hashlib
import inspect
import json
from pyflakes.api import check
import pg2522_current_strict_candidate_post as previous
from pg2658_operation_candidate_sources import SAVE, BEFORE, production
from pg1446_current_cold_stage import W

SLOT='pg2664-operation-unused-post-v1'


def payload(candidate=None):
    if candidate is None:candidate=json.loads((W/'pg2654-candidate-build-v1.safe.json').read_bytes())
    if type(candidate.get('actualExit'))is not int or candidate['actualExit']!=0 or candidate.get('candidateSource')!=production()or candidate.get('signatureVerified')is not True:raise ValueError('actual new signed candidate required')
    for k in ('manifestSha256','signatureSha256'):
        h=candidate.get(k)
        if type(h)is not str or len(h)!=64 or set(h)-set('0123456789abcdef'):raise ValueError('immutable digests required')
    path=W/'pg2656-current-a79-before-v1/payload.private.py';raw=path.read_text();receipt=json.loads((path.parent/'manifest.safe.json').read_bytes())
    if receipt['actualExit']!=0 or hashlib.sha256(raw.encode()).hexdigest()!=receipt['payloadSha256']:raise ValueError('actual current independent reader required')
    marker="save=base/'pg2656-current-a79-before-v1'"
    if raw.count(marker)!=1:raise ValueError('one actual readonly save boundary required')
    raw=raw[:raw.index(marker)];extra=previous.EXTRA
    for a,b in [('pg1684-completed-unused-placement-v4',SAVE),('9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37',BEFORE),
      ('PG1638','PG2654'),('pg1638','pg2654'),('2741c4546afad6c1e8b6efbd53dfb58144edf7bb',production()),
      ('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',candidate['manifestSha256']),
      ('5e32c12cc0231fd9ac307d3ffdfe6428aa53002e0398248cf32362d903d4aca5',candidate['signatureSha256'])]:extra=extra.replace(a,b)
    extra=extra.replace('genuineParentDone=true\\n','genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true\\n')
    raw+=extra+"require(native==json.loads((base/'pg2656-current-a79-before-v1/native-before.private.json').read_bytes()))\n"
    tree=ast.parse(inspect.getsource(previous.engine.payload));endings=[n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)and isinstance(n.value,str)and n.value.startswith("\nsave=base/'pg2150")]
    if len(endings)!=1:raise ValueError('one actual independent post result dialect required')
    raw+=endings[0].replace(previous.engine.SLOT,SLOT)
    if check(raw,'<whole new unused independent post>'):raise ValueError('all post namespace exports required')
    compile(raw,'<new operation unused independent post>','exec');return raw


def main():
    raw=inspect.getsource(previous.engine.main).replace('pg2146-place-v1.safe.json','pg2660-place-v1.safe.json')
    ns={**previous.engine.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<new unused placement post entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
