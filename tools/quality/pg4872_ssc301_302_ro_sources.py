"""Existing unused candidate to RO only; all72 current inputs remain protected."""
import inspect
import json
import pg3994_literal_invariant_ro_sources as previous
import pg4864_ssc301_302_unused_sources as unused
from immutable_payload_binding import bind_preserving_payloads

W=unused.W
CURRENT,SOURCE,BEFORE=unused.CURRENT,unused.SOURCE,unused.BEFORE
BOM=unused.candidate_bom()
TOOLS='pg4872-ssc301-302-ro-tools-v1'
SAVE='pg4876-ssc301-302-ro-completed-v1'
CLASS='Pg4872CandidateRo'
BASE=previous.BASE


def qualify():
    unused.qualify();outer=json.loads((W/'pg4870-ssc301-302-unused-post-v1/manifest.safe.json').read_bytes())
    r=outer.get('result',{})
    flags=('candidateUnusedOnly','candidate187SignatureVerified','current187SignatureVerified',
           'configuration32EveryFieldUnchanged','all24TablesEqualTwice','allClientAdvisoryMA0',
           'newTenReferencesReturnedNormally','native72Preserved','runtimeStartupAndApprovalEpochUnchanged')
    if not(type(outer.get('actualExit'))is int and outer['actualExit']==0 and type(r.get('actualExit'))is int and r['actualExit']==0
           and r.get('candidateSource')==SOURCE and r.get('currentSource')==CURRENT and r.get('candidateManifestSha256')==BOM and all(r.get(k)is True for k in flags)):
        raise ValueError('actual current825e/full72 and unused candidate187 independent post')
    return r


def bind(raw):
    raw=unused.role_text(raw)
    for a,b in [('pg3442-current-outbox-ro-tools-v1',TOOLS),('pg3446-current-outbox-ro-completed-v1',SAVE),
                ('pg3442','pg4872'),('Pg3442','Pg4872'),('PG3442','PG4872'),
                ('pg3444','pg4874'),('PG3444','PG4874'),('pg3446','pg4876'),('PG3446','PG4876')]:raw=raw.replace(a,b)
    return raw


def alias(raw):return bind_preserving_payloads(raw,lambda text:text.replace('pg4864','pg4872').replace('PG4864','PG4872'))


def sources(bom=BOM,before=BEFORE):
    ns={**vars(previous),'W':W,'CURRENT':CURRENT,'SOURCE':SOURCE,'BOM':BOM,'BEFORE':BEFORE,
        'TOOLS':TOOLS,'SAVE':SAVE,'CLASS':CLASS,'BASE':BASE,'qualify':qualify,
        'mapping':unused,'unused':unused,'bind':bind,'alias':alias}
    raw=inspect.getsource(previous.sources)
    for a,b in [('pg3994','pg4872'),('Pg3994','Pg4872'),('PG3994','PG4872'),('pg3982','pg4864'),('Pg3982','Pg4864'),('PG3982','PG4864')]:raw=raw.replace(a,b)
    exec(compile(raw,'<same current full72 candidate RO18>','exec'),ns);return ns['sources'](bom,before)


if __name__=='__main__':raise SystemExit('pure factory; no guest action')
