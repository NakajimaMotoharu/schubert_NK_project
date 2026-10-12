"""Separate unchanged current/oldfailure and all signed unused candidate bytes."""
import ast
import inspect
import json
import pg1849_warning_completed_current_before as engine
from pg1685_unused_candidate_independent_post import EXTRA as previous_extra
from pg1844_warning_unit_full_six import CANDIDATE

SLOT='pg1853-warning-unused-independent-post-v1'


def payload(post):
    candidate=json.loads((engine.W/'pg1846-candidate-build-v1.safe.json').read_bytes())
    before=json.loads((engine.W/'pg1849-warning-completed-current-before-v1/manifest.safe.json').read_bytes())
    if candidate['actualExit']!=0 or before['actualExit']!=0:raise ValueError('real candidate and sealed old source required')
    raw=engine.payload(post).replace(engine.SLOT,SLOT)
    extra=previous_extra
    for old,new in [('pg1684-completed-unused-placement-v4','pg1852-warning-unused-placement-v1'),('9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37',before['privateBeforeSha256']),('PG1638','PG1846'),('pg1638','pg1846'),('2741c4546afad6c1e8b6efbd53dfb58144edf7bb',CANDIDATE),('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',candidate['manifestSha256']),('5e32c12cc0231fd9ac307d3ffdfe6428aa53002e0398248cf32362d903d4aca5',candidate['signatureSha256'])]:extra=extra.replace(old,new)
    extra=extra.replace('genuineParentDone=true\\n','genuineParentWarningOriginal=true\\nmanagerFailureRetained=true\\n')
    marker="save=base/'"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one actual separate signed sibling post boundary required')
    raw=raw.replace(marker,extra+'\n'+marker)
    node=next(n for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Dict)and any(isinstance(k,ast.Constant)and k.value=='privateBeforeSha256'for k in n.keys))
    # Candidate identity is data, not the old deployed productionSource.
    text=ast.get_source_segment(raw,node)
    replacement=text[:-1]+",'unusedCandidate187Verified':True,'candidateSource':"+repr(CANDIDATE)+",'candidateManifestSha256':"+repr(candidate['manifestSha256'])+",'signatureVerified':True}"
    raw=raw.replace(text,replacement,1)
    compile(raw,'<old current whole and new unused signed 187 post>','exec');return raw


def main():
    actual=json.loads((engine.W/'pg1851-place-v2.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['sourceQualified']is not True or actual['currentApprovalEpochChanged']is not False:raise ValueError('actual sameSource new-only unused placement required')
    ns={**engine.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(engine.main),'<separate current/candidate post transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
