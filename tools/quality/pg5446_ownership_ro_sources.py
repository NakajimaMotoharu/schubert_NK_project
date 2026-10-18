"""RO-only296 graph after genuine unused post; all A2 full11/native88 preserved."""
import inspect
import hashlib
import json
import pg3994_literal_invariant_ro_sources as factory
import pg5438_ownership_unused_sources as unused
import pg5444_ownership_unused_post as post
from immutable_payload_binding import bind_preserving_payloads

W=unused.W
CURRENT,SOURCE,BEFORE=unused.CURRENT,unused.SOURCE,unused.BEFORE
BOM=unused.candidate_bom()
TOOLS='pg5446-ownership-ro-tools-v1'
SAVE='pg5450-ownership-ro-completed-v1'
CLASS='Pg5446CandidateRo'
BASE=factory.BASE


def qualify():
    unused.qualify();outer=json.loads((W/post.SLOT/'manifest.safe.json').read_bytes());r=outer.get('result',{})
    flags=('candidateUnusedOnly','candidate187SignatureVerified','current187SignatureVerified',
        'configuration32EveryFieldUnchanged','all24TablesEqualTwice','allClientAdvisoryMA0',
        'newTenReferencesReturnedNormally','native88Preserved','runtimeStartupAndApprovalEpochUnchanged')
    if not(type(outer.get('actualExit'))is int and outer['actualExit']==0 and outer['source']==CURRENT
        and type(r.get('actualExit'))is int and r['actualExit']==0 and r.get('candidateSource')==SOURCE
        and r.get('currentSource')==CURRENT and r.get('candidateManifestSha256')==BOM
        and r.get('full11BeforeSha256')==BEFORE and all(r.get(k)is True for k in flags)):
        raise ValueError('actual independent A2/full11/native88 and candidate296 unused post first')
    if outer['payloadSha256']!=hashlib.sha256(post.payload().encode()).hexdigest():
        raise ValueError('exact independent unused post source, never a flags-only substitute')
    return r


def bind(raw):
    raw=unused.role_text(raw)
    for old,new in(('pg3442-current-outbox-ro-tools-v1',TOOLS),('pg3446-current-outbox-ro-completed-v1',SAVE),
        ('pg3442','pg5446'),('Pg3442','Pg5446'),('PG3442','PG5446'),
        ('pg3444','pg5448'),('PG3444','PG5448'),('pg3446','pg5450'),('PG3446','PG5450')):
        raw=raw.replace(old,new)
    return raw


def alias(raw):return bind_preserving_payloads(raw,lambda text:text.replace('pg5438','pg5446').replace('PG5438','PG5446'))


def sources(bom=BOM,before=BEFORE):
    ns={**vars(factory),'W':W,'CURRENT':CURRENT,'SOURCE':SOURCE,'BOM':BOM,'BEFORE':BEFORE,
        'TOOLS':TOOLS,'SAVE':SAVE,'CLASS':CLASS,'BASE':BASE,'qualify':qualify,
        'mapping':unused,'unused':unused,'bind':bind,'alias':alias}
    raw=inspect.getsource(factory.sources)
    for old,new in(('pg3994','pg5446'),('Pg3994','Pg5446'),('PG3994','PG5446'),('pg3982','pg5438'),('Pg3982','Pg5438'),('PG3982','PG5438')):
        raw=raw.replace(old,new)
    exec(compile(raw,'<actual A2/full11/native88 RO18>','exec'),ns)
    return ns['sources'](bom,before)


if __name__=='__main__':raise SystemExit('pure factory; no guest operation')
