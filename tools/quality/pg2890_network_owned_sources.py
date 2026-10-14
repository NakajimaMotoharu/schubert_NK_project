"""New currenta9 ownedstop closed source graph, only actual sealed owners are authority."""
import inspect
import pg2708_operation_owned_sources as prior
import pg2878_network_newcurrent_terminal as terminal
from pg2862_network_newcurrent_observer import SOURCE,BOM
from pg2814_network_newboot_readonly import BOOT

TOOLS='pg2890-network-owned-stop-tools-v1'


def bind(raw):
    raw=prior.bind(raw)
    for a,b in [(prior.TOOLS,TOOLS),('pg2704-operation-current-full-seal-v1','pg2886-network-newcurrent-full-seal-v1'),
        ('pg2700-operation-current-terminal-v1',terminal.SLOT),('pg2686-operation-current-live-binding-v1','pg2874-network-newcurrent-live-binding-v1'),
        ('pg2706-operation-current-parent-projection-v1','pg2888-network-parent-projection-v1'),
        ('pg2712-operation-owned-stage-v1','pg2894-network-owned-stage-v1'),
        ('pg2716-operation-owned-post-v1','pg2898-network-owned-post-v1'),('PG2716-operation-owned-post-v1','PG2898-network-owned-post-v1'),
        ('pg2708','pg2890'),('Pg2708','Pg2890'),('PG2708','PG2890'),
        ('pg2710','pg2892'),('pg2712','pg2894'),('pg2713','pg2895'),('pg2714','pg2896'),
        ('PG2654','PG2802'),('pg2654','pg2802'),(prior.SOURCE,SOURCE),
        ('b2d6f605-61cf-425f-8fbd-12d606f6ee66',BOOT),('b2d6f60561cf425f8fbd12d606f6ee66',BOOT.replace('-',''))]:raw=raw.replace(a,b)
    return raw


def namespace():
    ns={**prior.previous.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'terminal_payload':terminal.payload,'candidate_bom':lambda:BOM}
    for fn in [prior.previous.context,prior.previous.emit_receipt,prior.previous.emit,prior.previous.sources]:
        exec(compile(bind(inspect.getsource(fn)),'<actual closed a9 owned graph>','exec'),ns)
    return ns


def context():return namespace()['context']()
def sources():return namespace()['sources']()
def emit(ctx,live,state,fields):return namespace()['emit'](ctx,live,state,fields,BOM)
