"""Normal unused-to-RO graph, current original remains historical data only."""
import inspect
import json
import pg3994_literal_invariant_ro_sources as old
import pg4706_ssc299_unused_sources as unused
from immutable_payload_binding import bind_preserving_payloads

W=unused.W
CURRENT,SOURCE,BEFORE=unused.CURRENT,unused.SOURCE,unused.BEFORE
BOM=unused.candidate_bom()
TOOLS='pg4714-ssc299-ro-tools-v1'
SAVE='pg4718-ssc299-ro-completed-v1'
CLASS='Pg4714CandidateRo'
BASE=old.BASE


def qualify():
    unused.qualify()
    outer=json.loads((W/'pg4712-ssc299-unused-post-v1/manifest.safe.json').read_bytes())
    result=outer.get('result',{})
    flags=['candidateUnusedOnly','candidate187SignatureVerified','current187SignatureVerified',
           'configuration32EveryFieldUnchanged','all24TablesEqualTwice','allClientAdvisoryMA0',
           'newTenReferencesReturnedNormally','native64Preserved','runtimeStartupAndApprovalEpochUnchanged']
    if not(type(outer.get('actualExit'))is int and outer['actualExit']==0
           and type(result.get('actualExit'))is int and result['actualExit']==0
           and result.get('candidateSource')==SOURCE and result.get('currentSource')==CURRENT
           and result.get('candidateManifestSha256')==BOM and all(result.get(f)is True for f in flags)):
        raise ValueError('actual normal current and independent unused candidate187 post required')
    return result


def bind(raw):
    raw=unused.role_text(raw)
    for before,after in [('pg3442-current-outbox-ro-tools-v1',TOOLS),('pg3446-current-outbox-ro-completed-v1',SAVE),
                         ('pg3442','pg4714'),('Pg3442','Pg4714'),('PG3442','PG4714'),
                         ('pg3444','pg4716'),('PG3444','PG4716'),('pg3446','pg4718'),('PG3446','PG4718')]:
        raw=raw.replace(before,after)
    return raw


def alias(raw):
    return bind_preserving_payloads(raw,lambda text:text.replace('pg4706','pg4714').replace('PG4706','PG4714'))


def sources(bom=BOM,before=BEFORE):
    ns={**vars(old),'W':W,'CURRENT':CURRENT,'SOURCE':SOURCE,'BOM':BOM,'BEFORE':BEFORE,
        'TOOLS':TOOLS,'SAVE':SAVE,'CLASS':CLASS,'BASE':BASE,'qualify':qualify,
        'mapping':unused,'unused':unused,'bind':bind,'alias':alias}
    raw=inspect.getsource(old.sources)
    for a,b in [('pg3994','pg4714'),('Pg3994','Pg4714'),('PG3994','PG4714'),
                ('pg3982','pg4706'),('Pg3982','Pg4706'),('PG3982','PG4706')]:raw=raw.replace(a,b)
    exec(compile(raw,'<normal current candidate RO graph>','exec'),ns)
    return ns['sources'](bom,before)


if __name__=='__main__':raise SystemExit('pure factory; no VM action')
