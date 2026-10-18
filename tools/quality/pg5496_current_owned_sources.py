"""Normal296 owned graph; exact newday/Browser capsules preserved, historical tuples not permits."""
import types
import json
import pg5060_current_owned_sources as previous
import pg5476_current_admission_image as admission
import pg5478_current_genuine_terminal as acceptance
import pg5524_guest_clock_same_owner_browser as actual
import pg5526_guest_clock_browser_composite as composite
import pg5528_guest_clock_parent_projection as projection
from immutable_payload_binding import bind_preserving_payloads

SOURCE,BOM=admission.SOURCE,admission.BOM
TOOLS='pg5496-current-owned-tools-v1'


def composite_payload(binding):return composite.payload(binding)


class Current:
    SOURCE=SOURCE;BOM=BOM;SEAL=composite.SLOT;TERM=acceptance.TERM
    terminal_payload=staticmethod(acceptance.payload)
    seal_payload=staticmethod(composite_payload)


current=Current


def role_text(raw):
    for old,new in((previous.SOURCE,SOURCE),(previous.BOM,BOM),(previous.TOOLS,TOOLS),
        (previous.composite.SLOT,composite.SLOT),(previous.acceptance.TERM,acceptance.TERM),
        (previous.admission.LIVE,admission.LIVE),(previous.projection.SLOT,projection.SLOT),
        ('PG4980','PG5430'),('pg4980','pg5430'),
        ('pg5064-current-owned-stage-v1','pg5500-current-owned-stage-v1'),
        ('pg5066-current-owned-post-v1','pg5502-current-owned-post-v1'),
        ('PG5066-current-owned-post-v1','PG5502-current-owned-post-v1'),
        ('pg5060','pg5496'),('Pg5060','Pg5496'),('PG5060','PG5496'),
        ('pg5062','pg5498'),('pg5064','pg5500'),('pg5065','pg5501')):
        raw=raw.replace(old,new)
    return raw


def bind(raw):return bind_preserving_payloads(previous.bind(raw),role_text)


def final_bind(raw):return bind_preserving_payloads(previous.final_bind(raw),role_text)


def candidate_bom():return BOM


def namespace():
    ns={**vars(previous),'SOURCE':SOURCE,'BOM':BOM,'TOOLS':TOOLS,'bind':bind,'current':current,
        'candidate_bom':candidate_bom,'acceptance':acceptance}
    return types.FunctionType(previous.namespace.__code__,ns)()


def context():
    ns={**vars(previous),'actual':actual,'composite':composite,'acceptance':acceptance}
    return types.FunctionType(previous.context.__code__,ns)()


def emit(ctx,binding,state,fields):
    ns={**vars(previous),'final_bind':final_bind,'namespace':namespace}
    return types.FunctionType(previous.emit.__code__,ns)(ctx,binding,state,fields)


def sources():
    b=admission.live();bound={'binding':{k:v for k,v in b.items()if k!='rootPid'},'rootPid':b['rootPid']}
    term=actual.receipt(acceptance.TERM);proof=json.loads((admission.W/projection.SLOT/'manifest.safe.json').read_bytes());ctx=context()
    if not(type(proof['actualExit'])is int and proof['actualExit']==0 and proof['source']==SOURCE and proof['result']['sealedBeforeSha256']==ctx[0]):
        raise ValueError('actual same296 exact parent18 projection first')
    return emit(ctx,bound,term['parentState'],proof['result']['parentState18'])
