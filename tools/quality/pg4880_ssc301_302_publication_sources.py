"""Finite code-only publication; old current completed tuple is data only."""
import inspect
import json
import pg4002_literal_invariant_publication_sources as previous
import pg4872_ssc301_302_ro_sources as ro
from immutable_payload_binding import bind_preserving_payloads

W=ro.W
CURRENT,CURRENT_BOM,SOURCE,BOM,BEFORE,BOOT=ro.CURRENT,ro.unused.CURRENT_BOM,ro.SOURCE,ro.BOM,ro.BEFORE,ro.unused.BOOT
TOOLS='pg4880-ssc301-302-publication-tools-v1'
SAVE='pg4884-ssc301-302-publication-v1'
CLASS='Pg4880OrdinaryPublication'
BASE=previous.BASE


def qualify():
    ro.qualify();outer=json.loads((W/'pg4878-ssc301-302-ro-independent-post-v1/manifest.safe.json').read_bytes())
    r=outer.get('result',{})
    if not(type(outer.get('actualExit'))is int and outer['actualExit']==0 and type(r.get('actualExit'))is int and r['actualExit']==0
           and r.get('candidateHostReadonlyVerified')is True and r.get('candidateSource')==SOURCE
           and r.get('currentSource')==CURRENT and r.get('candidateManifestSha256')==BOM
           and r.get('allClientAdvisoryMA0')is True and r.get('newTenReferencesReturnedNormally')is True
           and r.get('native72Preserved')is True):
        raise ValueError('actual same candidate PID1RO/full72 independent post first')
    return r


def bind(raw):
    raw=ro.unused.role_text(raw)
    for a,b in [('pg3450-current-outbox-publication-tools-v1',TOOLS),('pg3456-current-outbox-publication-v1',SAVE),
                ('pg3446-current-outbox-ro-completed-v1',ro.SAVE),('pg3450','pg4880'),('Pg3450','Pg4880'),('PG3450','PG4880'),
                ('pg3452','pg4882'),('PG3452','PG4882'),('pg3454','pg4884'),('PG3454','PG4884')]:raw=raw.replace(a,b)
    return raw


def alias(raw):return bind_preserving_payloads(raw,lambda text:text.replace('pg4872','pg4880').replace('PG4872','PG4880'))


def sources(bom=BOM,before=BEFORE):
    ns={**vars(previous),'W':W,'CURRENT':CURRENT,'SOURCE':SOURCE,'BOM':BOM,'BEFORE':BEFORE,
        'TOOLS':TOOLS,'SAVE':SAVE,'CLASS':CLASS,'BASE':BASE,'qualify':qualify,
        'mapping':ro.unused,'ro':ro,'bind':bind,'alias':alias}
    raw=inspect.getsource(previous.sources)
    for a,b in [('pg4002','pg4880'),('Pg4002','Pg4880'),('PG4002','PG4880'),('pg3994','pg4872'),('Pg3994','Pg4872'),('PG3994','PG4872')]:raw=raw.replace(a,b)
    exec(compile(raw,'<finite source-only publication24>','exec'),ns);return ns['sources'](bom,before)


if __name__=='__main__':raise SystemExit('pure factory; no guest action')
