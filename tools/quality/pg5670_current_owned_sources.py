"""Same0ea normal owned graph; Root/Browser capsules and prior94 native are immutable."""
import json
import types
import pg5496_current_owned_sources as previous
import pg5644_current_admission_image as admission
import pg5646_current_genuine_terminal as acceptance
import pg5662_current_same_owner_browser as actual
import pg5664_current_browser_composite as composite
import pg5666_current_parent_projection as projection
from immutable_payload_binding import bind_preserving_payloads

SOURCE,BOM=admission.SOURCE,admission.BOM
TOOLS='pg5670-current-owned-tools-v1'


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
      ('PG5430','PG5598'),('pg5430','pg5598'),('pg5496','pg5670'),('Pg5496','Pg5670'),('PG5496','PG5670'),
      ('pg5498','pg5672'),('pg5500','pg5674'),('PG5500','PG5674'),('pg5501','pg5675'),
      ('pg5502','pg5676'),('PG5502','PG5676'),('pg5063-parent-two-source-prequalification-v1','pg5673-parent-two-source-prequalification-v1')):
        raw=raw.replace(old,new)
    return raw


def bind(raw):return bind_preserving_payloads(previous.bind(raw),role_text)


def final_bind(raw):return bind_preserving_payloads(previous.final_bind(raw),role_text)


def candidate_bom():return BOM


def namespace():
    ns={**vars(previous.previous),'SOURCE':SOURCE,'BOM':BOM,'TOOLS':TOOLS,'bind':bind,'current':current,
      'candidate_bom':candidate_bom,'acceptance':acceptance}
    return types.FunctionType(previous.previous.namespace.__code__,ns)()


def context():
    ns={**vars(previous.previous),'actual':actual,'composite':composite,'acceptance':acceptance}
    return types.FunctionType(previous.previous.context.__code__,ns)()


def emit(ctx,binding,state,fields):
    ns={**vars(previous.previous),'final_bind':final_bind,'namespace':namespace}
    return types.FunctionType(previous.previous.emit.__code__,ns)(ctx,binding,state,fields)


def sources():
    b=admission.live();bound={'binding':{k:v for k,v in b.items()if k!='rootPid'},'rootPid':b['rootPid']}
    term=actual.receipt(acceptance.TERM);proof=json.loads((admission.W/projection.SLOT/'manifest.safe.json').read_bytes());ctx=context()
    if not(type(proof['actualExit'])is int and proof['actualExit']==0 and proof['source']==SOURCE and proof['result']['sealedBeforeSha256']==ctx[0]):raise ValueError('actual same0ea exactparent18 first')
    return emit(ctx,bound,term['parentState'],proof['result']['parentState18'])
