"""Normal same-source owned graph; immutable snapshots/oracles never role-rebound."""
import inspect
import json
import pg4282_current_owned_sources as previous
import pg3490_outbox_owned_sources as composer
import pg4752_new_current_admission_image as admission
import pg4754_new_current_terminal as acceptance
import pg4764_new_current_same_owner_browser as actual
import pg4768_new_current_browser_composite as composite
import pg4770_new_current_parent_projection as projection
from immutable_payload_binding import bind_preserving_payloads

SOURCE,BOM=admission.SOURCE,admission.BOM
TOOLS='pg4772-new-current-owned-tools-v1'


def composite_payload(binding):return composite.payload(binding)


class Current:
    SOURCE=SOURCE;BOM=BOM;SEAL=composite.SLOT;TERM=acceptance.TERM
    terminal_payload=staticmethod(acceptance.payload)
    seal_payload=staticmethod(composite_payload)


current=Current


def role_text(raw):
    pairs=[(previous.SOURCE,SOURCE),(previous.BOM,BOM),(previous.TOOLS,TOOLS),
           (previous.composite.SLOT,composite.SLOT),(previous.acceptance.TERM,acceptance.TERM),
           (previous.acceptance.admission.LIVE,admission.LIVE),(previous.projection.SLOT,projection.SLOT),
           ('PG3976','PG4702'),('pg3976','pg4702'),
           ('pg4286-current-owned-stage-v1','pg4776-new-current-owned-stage-v1'),
           ('pg4288-current-owned-post-v1','pg4778-new-current-owned-post-v1'),
           ('PG4288-current-owned-post-v1','PG4778-new-current-owned-post-v1'),
           ('pg4282','pg4772'),('Pg4282','Pg4772'),('PG4282','PG4772'),
           ('pg4284','pg4774'),('pg4286','pg4776'),('pg4287','pg4777'),('pg4289','pg4779')]
    for old,new in pairs:raw=raw.replace(old,new)
    return raw


def bind(raw):return bind_preserving_payloads(previous.bind(raw),role_text)


def final_bind(raw):return bind_preserving_payloads(previous.final_bind(raw),role_text)


def candidate_bom():return BOM


def namespace():
    values={**vars(composer),'SOURCE':SOURCE,'BOM':BOM,'TOOLS':TOOLS,'bind':bind,'current':current,'candidate_bom':candidate_bom}
    exec(compile(inspect.getsource(composer.namespace),'<new normal owned graph>','exec'),values)
    result=values['namespace']();result['terminal_payload']=acceptance.payload;return result


def context():
    seal,term=actual.receipt(composite.SLOT),actual.receipt(acceptance.TERM)
    if not(seal['sqlOracleQualified']and seal['currentFourOwnedLive']and term['normalUnit0or10']and seal['businessOracle']['exactRootBrowserCurrentChain']):raise ValueError('genuine normal Root/Browser/full24/current chain first')
    return seal['privateBeforeSha256'],seal['observedOwned'],seal['genuineCompletion'],seal['doneEndUtc']


def emit(ctx,binding,state,fields):return {final_bind(n):final_bind(raw)for n,raw in namespace()['emit'](ctx,binding,state,fields).items()}


def sources():
    b=admission.live();binding={'binding':{k:v for k,v in b.items()if k!='rootPid'},'rootPid':b['rootPid']}
    term=actual.receipt(acceptance.TERM);proof=json.loads((admission.W/projection.SLOT/'manifest.safe.json').read_bytes());ctx=context()
    if not(type(proof['actualExit'])is int and proof['actualExit']==0 and proof['source']==SOURCE and proof['result']['sealedBeforeSha256']==ctx[0]):raise ValueError('actual same-current parent18 projection')
    return emit(ctx,binding,term['parentState'],proof['result']['parentState18'])
