"""Normal finite code-only publication; never reuses old Root as new authority."""
import inspect
import json
import pg4002_literal_invariant_publication_sources as old
import pg4714_ssc299_ro_sources as ro
from immutable_payload_binding import bind_preserving_payloads

W=ro.W
CURRENT,CURRENT_BOM,SOURCE,BOM,BEFORE,BOOT=ro.CURRENT,ro.unused.CURRENT_BOM,ro.SOURCE,ro.BOM,ro.BEFORE,ro.unused.BOOT
TOOLS='pg4722-ssc299-publication-tools-v1'
SAVE='pg4726-ssc299-publication-v1'
CLASS='Pg4722OrdinaryPublication'
BASE=old.BASE


def qualify():
    ro.qualify()
    outer=json.loads((W/'pg4720-ssc299-ro-independent-post-v1/manifest.safe.json').read_bytes())
    r=outer.get('result',{})
    if not(type(outer.get('actualExit'))is int and outer['actualExit']==0
           and type(r.get('actualExit'))is int and r['actualExit']==0
           and r.get('candidateHostReadonlyVerified')is True and r.get('candidateSource')==SOURCE
           and r.get('currentSource')==CURRENT and r.get('candidateManifestSha256')==BOM
           and r.get('allClientAdvisoryMA0')is True and r.get('newTenReferencesReturnedNormally')is True):
        raise ValueError('genuine normal current/readonly candidate full independent post first')
    return r


def bind(raw):
    raw=ro.unused.role_text(raw)
    for before,after in [('pg3450-current-outbox-publication-tools-v1',TOOLS),('pg3456-current-outbox-publication-v1',SAVE),
                         ('pg3446-current-outbox-ro-completed-v1',ro.SAVE),
                         ('pg3450','pg4722'),('Pg3450','Pg4722'),('PG3450','PG4722'),
                         ('pg3452','pg4724'),('PG3452','PG4724'),('pg3454','pg4726'),('PG3454','PG4726')]:
        raw=raw.replace(before,after)
    return raw


def alias(raw):
    return bind_preserving_payloads(raw,lambda text:text.replace('pg4714','pg4722').replace('PG4714','PG4722'))


def sources(bom=BOM,before=BEFORE):
    ns={**vars(old),'W':W,'CURRENT':CURRENT,'SOURCE':SOURCE,'BOM':BOM,'BEFORE':BEFORE,
        'TOOLS':TOOLS,'SAVE':SAVE,'CLASS':CLASS,'BASE':BASE,'qualify':qualify,
        'mapping':ro.unused,'ro':ro,'bind':bind,'alias':alias}
    raw=inspect.getsource(old.sources)
    for a,b in [('pg4002','pg4722'),('Pg4002','Pg4722'),('PG4002','PG4722'),
                ('pg3994','pg4714'),('Pg3994','Pg4714'),('PG3994','PG4714')]:raw=raw.replace(a,b)
    exec(compile(raw,'<normal finite source-only publication graph>','exec'),ns)
    return ns['sources'](bom,before)


if __name__=='__main__':raise SystemExit('pure factory; no VM action')
