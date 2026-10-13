"""Independent retained-current full read plus unused new signed187, no publication."""
import ast
import hashlib
import inspect
import json
from pyflakes.api import check
import pg2150_normal_unused_independent_post as prior
from pg1685_unused_candidate_independent_post import EXTRA
from pg2412_question_unused_sources import SAVE,BEFORE,production
from pg1446_current_cold_stage import W

SLOT = 'pg2418-question-unused-independent-post-v1'


def payload(candidate=None):
    if candidate is None:
        candidate = json.loads((W/'pg2428-candidate-build-v1.safe.json').read_bytes())
    if candidate.get('actualExit') != 0 or candidate.get('candidateSource') != production() or candidate.get('signatureVerified') is not True:
        raise ValueError('actual new signed candidate required')
    for k in ['manifestSha256','signatureSha256']:
        value=candidate.get(k)
        if type(value) is not str or len(value) != 64 or set(value)-set('0123456789abcdef'):
            raise ValueError('actual immutable candidate digests required')
    path=W/'pg2410-retired-current-before-v1/payload.private.py'
    raw=path.read_text();m=json.loads((path.parent/'manifest.safe.json').read_bytes())
    if m['actualExit'] != 0 or hashlib.sha256(raw.encode()).hexdigest() != m['payloadSha256']:
        raise ValueError('actual full independent current reader unchanged required')
    marker="save=base/'pg2410-retired-current-before-v1'"
    if raw.count(marker) != 1:
        raise ValueError('one independent readonly current save boundary required')
    raw=raw[:raw.index(marker)]
    extra=EXTRA
    for a,b in [('pg1684-completed-unused-placement-v4',SAVE),
                ('9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37',BEFORE),
                ('PG1638','PG2428'),('pg1638','pg2428'),
                ('2741c4546afad6c1e8b6efbd53dfb58144edf7bb',production()),
                ('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',candidate['manifestSha256']),
                ('5e32c12cc0231fd9ac307d3ffdfe6428aa53002e0398248cf32362d903d4aca5',candidate['signatureSha256'])]:
        extra=extra.replace(a,b)
    extra=extra.replace('genuineParentDone=true\\n','genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true\\n')
    raw+=extra
    raw+="require(native==json.loads((base/'pg2410-retired-current-before-v1/native-before.private.json').read_bytes()))\n"
    ending=inspect.getsource(prior.payload)
    # Reuse only the explicit independent result/save statements, not the old
    # candidate input or historical current source/receipt.
    tree=ast.parse(ending)
    nodes=[n for n in ast.walk(tree) if isinstance(n,ast.Constant)
           and isinstance(n.value,str) and n.value.startswith("\nsave=base/'pg2150")]
    if len(nodes)!=1:
        raise ValueError('one independent result dialect required')
    raw+=nodes[0].value.replace(prior.SLOT,SLOT)
    if check(raw,'<independent new question unused full post>'):
        raise ValueError('all current and candidate post globals required')
    compile(raw,'<independent candidate full post>','exec')
    return raw


def main():
    raw=inspect.getsource(prior.main).replace('pg2146-place-v1.safe.json','pg2414-place-v1.safe.json')
    namespace={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<new candidate immutable place post>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':
    raise SystemExit(main())
