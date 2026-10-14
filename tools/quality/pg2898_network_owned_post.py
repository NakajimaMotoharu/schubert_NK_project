"""Separate actual full currenta9 ownedstop resource/rawdata/native post; no operations."""
import inspect
import pg2716_operation_owned_post as prior
from pg2890_network_owned_sources import context,TOOLS,SOURCE,bind
from pg2862_network_newcurrent_observer import BOM

SLOT='pg2898-network-owned-post-v1'


def namespace():
    ns={**prior.previous.__dict__,'context':context,'TOOLS':TOOLS,'SOURCE':SOURCE,'SLOT':SLOT,'candidate_bom':lambda:BOM}
    for fn in [prior.previous.emit,prior.previous.payload,prior.previous.entry]:
        exec(compile(bind(inspect.getsource(fn)),'<actual a9 independent post graph>','exec'),ns)
    original_emit=ns['emit']
    ns['emit']=lambda *a,**kw:bind(original_emit(*a,**kw))
    # First actual stop belongs to the new-only dispatch v2, not refusedstagev1.
    return ns


def emit(seals,ctx,live):return namespace()['emit'](seals,ctx,live,BOM)
def payload(seals):return namespace()['payload'](seals)
def entry():
    ns=namespace()
    raw=inspect.getsource(prior.previous.entry)
    raw=bind(raw).replace("('pg2038-stop-v1', 'pg2894-stop-v1')","('pg2038-stop-v1', 'pg2894-stop-v2')")
    exec(compile(raw,'<new actual independent post v2 stop receipt>','exec'),ns)
    return ns['entry']()


if __name__=='__main__':raise SystemExit(entry()())
