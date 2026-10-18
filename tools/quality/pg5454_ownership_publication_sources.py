"""Finite code-only296 publication after genuine PID1RO; oldA2 Root/native stays history."""
import inspect
import hashlib
import json
import pg4002_literal_invariant_publication_sources as factory
import pg5446_ownership_ro_sources as ro
import pg5452_ownership_ro_post as ro_post
from immutable_payload_binding import bind_preserving_payloads

W=ro.W
CURRENT,CURRENT_BOM,SOURCE,BOM,BEFORE,BOOT=ro.CURRENT,ro.unused.CURRENT_BOM,ro.SOURCE,ro.BOM,ro.BEFORE,ro.unused.BOOT
TOOLS='pg5454-ownership-publication-tools-v1'
SAVE='pg5458-ownership-publication-v1'
CLASS='Pg5454OrdinaryPublication'
BASE=factory.BASE


def qualify():
    ro.qualify();outer=json.loads((W/ro_post.SLOT/'manifest.safe.json').read_bytes());r=outer.get('result',{})
    if not(type(outer.get('actualExit'))is int and outer['actualExit']==0 and outer['source']==CURRENT
        and type(r.get('actualExit'))is int and r['actualExit']==0 and r.get('candidateHostReadonlyVerified')is True
        and r.get('candidateSource')==SOURCE and r.get('currentSource')==CURRENT and r.get('candidateManifestSha256')==BOM
        and r.get('allClientAdvisoryMA0')is True and r.get('newTenReferencesReturnedNormally')is True
        and r.get('native88Preserved')is True and r.get('full11BeforeSha256')==BEFORE):
        raise ValueError('genuine same296 PID1RO/full11/native88 independent post first')
    if outer['payloadSha256']!=hashlib.sha256(ro_post.payload().encode()).hexdigest():raise ValueError('exact original RO independent reader')
    return r


def bind(raw):
    raw=ro.unused.role_text(raw)
    for old,new in(('pg3450-current-outbox-publication-tools-v1',TOOLS),('pg3456-current-outbox-publication-v1',SAVE),
        ('pg3446-current-outbox-ro-completed-v1',ro.SAVE),('pg3450','pg5454'),('Pg3450','Pg5454'),('PG3450','PG5454'),
        ('pg3452','pg5456'),('PG3452','PG5456'),('pg3454','pg5458'),('PG3454','PG5458')):
        raw=raw.replace(old,new)
    return raw


def alias(raw):return bind_preserving_payloads(raw,lambda text:text.replace('pg5446','pg5454').replace('PG5446','PG5454'))


def sources(bom=BOM,before=BEFORE):
    ns={**vars(factory),'W':W,'CURRENT':CURRENT,'SOURCE':SOURCE,'BOM':BOM,'BEFORE':BEFORE,'TOOLS':TOOLS,
        'SAVE':SAVE,'CLASS':CLASS,'BASE':BASE,'qualify':qualify,'mapping':ro.unused,'ro':ro,'bind':bind,'alias':alias}
    raw=inspect.getsource(factory.sources)
    for old,new in(('pg4002','pg5454'),('Pg4002','Pg5454'),('PG4002','PG5454'),('pg3994','pg5446'),('Pg3994','Pg5446'),('PG3994','PG5446')):
        raw=raw.replace(old,new)
    exec(compile(raw,'<all24 A2/296 finite code-only roles>','exec'),ns)
    return ns['sources'](bom,before)


if __name__=='__main__':raise SystemExit('pure factory; no guest action')
