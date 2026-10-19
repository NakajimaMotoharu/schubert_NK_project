"""Finite code-only0ea publication after genuine RO; previous296/native stays history."""
import hashlib
import inspect
import json
import pg5454_ownership_publication_sources as previous
import pg5616_current_ro_sources as ro
import pg5622_current_ro_post as ro_post
from immutable_payload_binding import bind_preserving_payloads

W=ro.W
CURRENT,CURRENT_BOM,SOURCE,BOM,BEFORE,BOOT=ro.CURRENT,ro.unused.CURRENT_BOM,ro.SOURCE,ro.BOM,ro.BEFORE,ro.unused.BOOT
TOOLS='pg5624-current-publication-tools-v1'
SAVE='pg5628-current-publication-v1'
CLASS='Pg5624OrdinaryPublication'
BASE=previous.BASE


def qualify():
    ro.qualify();raw=(W/ro_post.SLOT/'manifest.safe.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!='e61c618ca4165955ff6cc01fed8125c66a9477cf1e41fc74b13c38d923247425':raise ValueError('immutable original RO post')
    outer=json.loads(raw);r=outer['result']
    if not(type(outer['actualExit'])is int and outer['actualExit']==0 and outer['source']==CURRENT and r['actualExit']==0
      and r['candidateHostReadonlyVerified']is True and r['candidateSource']==SOURCE and r['productionSource']==CURRENT
      and r['candidateManifestSha256']==BOM and r['allClientAdvisoryFlock0']is True and r['allKernelActor0']is True
      and r['allTenRefsReturnedNormally']is True and r['nativePhysicalFiles']==94 and r['full11BeforeSha256']==r['privateAfterSha256']==BEFORE):raise ValueError('actual distinct-source PID1 RO/full11/native94 first')
    if outer['payloadSha256']!=hashlib.sha256(ro_post.payload().encode()).hexdigest():raise ValueError('exact independent RO source')
    return r


def bind(raw):
    raw=ro.unused.role_text(raw)
    for old,new in(('pg3450-current-outbox-publication-tools-v1',TOOLS),('pg3456-current-outbox-publication-v1',SAVE),
      ('pg3446-current-outbox-ro-completed-v1',ro.SAVE),('pg3450','pg5624'),('Pg3450','Pg5624'),('PG3450','PG5624'),
      ('pg3452','pg5626'),('PG3452','PG5626'),('pg3454','pg5628'),('PG3454','PG5628')):raw=raw.replace(old,new)
    return raw


def alias(raw):return bind_preserving_payloads(raw,lambda text:text.replace('pg5616','pg5624').replace('PG5616','PG5624'))


def sources(bom=BOM,before=BEFORE):
    factory=previous.factory
    scope={**vars(factory),'W':W,'CURRENT':CURRENT,'SOURCE':SOURCE,'BOM':BOM,'BEFORE':BEFORE,'TOOLS':TOOLS,
      'SAVE':SAVE,'CLASS':CLASS,'BASE':BASE,'qualify':qualify,'mapping':ro.unused,'ro':ro,'bind':bind,'alias':alias}
    raw=inspect.getsource(factory.sources)
    for old,new in(('pg4002','pg5624'),('Pg4002','Pg5624'),('PG4002','PG5624'),('pg3994','pg5616'),('Pg3994','Pg5616'),('PG3994','PG5616')):raw=raw.replace(old,new)
    exec(compile(raw,'<all24 current296/candidate0ea finite code-only roles>','exec'),scope)
    return scope['sources'](bom,before)


if __name__=='__main__':raise SystemExit('pure factory; no guest operation')
