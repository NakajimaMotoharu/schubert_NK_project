"""Current genuine composite/parent18 owned graph; never change protected oracle/data literals."""
import json
import pg4042_literal_invariant_owned_sources as previous
import pg4252_current_independent_acceptance as acceptance
import pg4272_current_browser_composite as composite
import pg4270_current_same_owner_browser as actual
import pg4280_current_parent_projection as projection
from pg4260_stable_admission_image import SOURCE,BOM,live
from pg1446_current_cold_stage import W
from immutable_payload_binding import bind_preserving_payloads

TOOLS='pg4282-current-owned-tools-v1'


class Current:
    SOURCE=SOURCE;BOM=BOM;SEAL=composite.SLOT;TERM=acceptance.TERM
    terminal_payload=staticmethod(acceptance.terminal_payload)
    seal_payload=staticmethod(composite.payload)


current=Current


def role_text(raw):
    for old,new in [(previous.TOOLS,TOOLS),(previous.composite.SLOT,composite.SLOT),
       (previous.acceptance.TERM,acceptance.TERM),(previous.acceptance.LIVE,acceptance.admission.LIVE),
       ('pg4040-literal-invariant-parent-projection-v1',projection.SLOT),
       ('pg4046-literal-invariant-owned-stage-v1','pg4286-current-owned-stage-v1'),
       ('pg4048-literal-invariant-owned-post-v1','pg4288-current-owned-post-v1'),
       ('PG4048-literal-invariant-owned-post-v1','PG4288-current-owned-post-v1'),
       ('pg4042','pg4282'),('Pg4042','Pg4282'),('PG4042','PG4282'),
       ('pg4044','pg4284'),('pg4046','pg4286'),('pg4047','pg4287'),('pg4049','pg4289')]:raw=raw.replace(old,new)
    return raw


def bind(raw):return bind_preserving_payloads(previous.bind(raw),role_text)


def final_bind(raw):return bind_preserving_payloads(previous.final_bind(raw),role_text)


def candidate_bom():return BOM


def context():
    seal,term=actual.receipt(composite.SLOT),actual.receipt(acceptance.TERM)
    if not(seal['sqlOracleQualified']and seal['currentFourOwnedLive']and term['normalUnit0or10']and seal['businessOracle']['exactRootBrowserCurrentChain']):raise ValueError('actual complete current Root/Browser/current chain required')
    return seal['privateBeforeSha256'],seal['observedOwned'],seal['genuineCompletion'],seal['doneEndUtc']


def emit(ctx,binding,state,fields):
    ns=previous.namespace();ns['terminal_payload']=acceptance.terminal_payload
    return {final_bind(name):final_bind(raw)for name,raw in ns['emit'](ctx,binding,state,fields).items()}


def sources():
    binding=live();qualified={'binding':{k:v for k,v in binding.items()if k!='rootPid'},'rootPid':binding['rootPid']}
    term=actual.receipt(acceptance.TERM)
    p=json.loads((W/projection.SLOT/'manifest.safe.json').read_bytes());ctx=context()
    if p['actualExit']!=0 or p['source']!=SOURCE or p['result']['sealedBeforeSha256']!=ctx[0]:raise ValueError('actual same composite projection required')
    return emit(ctx,qualified,term['parentState'],p['result']['parentState18'])
