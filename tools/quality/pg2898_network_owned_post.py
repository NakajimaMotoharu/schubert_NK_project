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
    return ns


def emit(seals,ctx,live):return namespace()['emit'](seals,ctx,live,BOM)
def payload(seals):return namespace()['payload'](seals)
def entry():return namespace()['entry']()


if __name__=='__main__':raise SystemExit(entry()())
