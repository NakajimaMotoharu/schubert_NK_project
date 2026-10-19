"""RO-only candidate0ea after actual unused post; current296 full11/native94 preserved."""
import hashlib
import inspect
import json
import pg5446_ownership_ro_sources as previous
import pg5608_current_unused_sources as unused
import pg5614_current_unused_post as post
from immutable_payload_binding import bind_preserving_payloads

W=unused.W
CURRENT,SOURCE,BEFORE=unused.CURRENT,unused.SOURCE,unused.BEFORE
BOM=unused.candidate_bom()
TOOLS='pg5616-current-ro-tools-v1'
SAVE='pg5620-current-ro-completed-v1'
CLASS='Pg5616CandidateRo'
BASE=previous.BASE


def qualify():
    unused.qualify();path=W/post.SLOT/'manifest.safe.json';raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!='2e13c88651848101e83857f9a4e398b0427eabaf723751c2e999cb36c103757a':raise ValueError('immutable actual unused post, never a flags substitute')
    outer=json.loads(raw);r=outer['result']
    flags=('candidateUnusedOnly','candidate187SignatureVerified','allFull11BeforeAfterEqual','all24EqualTwice','allTenRefsReturnedNormally',
      'all92OriginalAndTenCatalogUnionPreserved','freshPid1HistoryMatches','allOriginalBackupCredentialTreesUnchanged','allClientAdvisoryFlock0','allKernelActor0','startsStopsReloadsSqlWrites0')
    if not(type(outer['actualExit'])is int and outer['actualExit']==0 and outer['source']==CURRENT and r['actualExit']==0
      and r['productionSource']==CURRENT and r['candidateSource']==SOURCE and r['candidateManifestSha256']==BOM
      and r['privateAfterSha256']==r['full11BeforeSha256']==BEFORE and r['nativePhysicalFiles']==94 and all(r[k]is True for k in flags)):
        raise ValueError('actual current296/full11/native94 and distinct unused0ea post first')
    if outer['payloadSha256']!=hashlib.sha256(post.payload().encode()).hexdigest():raise ValueError('exact independent source-bound unused post')
    return r


def bind(raw):
    raw=unused.role_text(raw)
    for old,new in(('pg3442-current-outbox-ro-tools-v1',TOOLS),('pg3446-current-outbox-ro-completed-v1',SAVE),
      ('pg3442','pg5616'),('Pg3442','Pg5616'),('PG3442','PG5616'),('pg3444','pg5618'),('PG3444','PG5618'),('pg3446','pg5620'),('PG3446','PG5620')):raw=raw.replace(old,new)
    return raw


def alias(raw):return bind_preserving_payloads(raw,lambda text:text.replace('pg5608','pg5616').replace('PG5608','PG5616'))


def sources(bom=BOM,before=BEFORE):
    factory=previous.factory
    scope={**vars(factory),'W':W,'CURRENT':CURRENT,'SOURCE':SOURCE,'BOM':BOM,'BEFORE':BEFORE,'TOOLS':TOOLS,'SAVE':SAVE,'CLASS':CLASS,
      'BASE':BASE,'qualify':qualify,'mapping':unused,'unused':unused,'bind':bind,'alias':alias}
    raw=inspect.getsource(factory.sources)
    for old,new in(('pg3994','pg5616'),('Pg3994','Pg5616'),('PG3994','PG5616'),('pg3982','pg5608'),('Pg3982','Pg5608'),('PG3982','PG5608')):raw=raw.replace(old,new)
    exec(compile(raw,'<actual296/full11/native94 RO18>','exec'),scope)
    return scope['sources'](bom,before)


if __name__=='__main__':raise SystemExit('pure factory; no guest operation')
