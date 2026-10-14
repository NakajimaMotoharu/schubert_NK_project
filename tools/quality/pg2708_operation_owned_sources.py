"""New owned stop source graph; only actual new sealed identities are authority."""
import inspect
import pg2554_strict_current_owned_sources as previous
from pg2700_operation_current_terminal import payload as terminal_payload
from pg2674_operation_publication_sources import production,candidate_bom

SOURCE=production();TOOLS='pg2708-operation-owned-stop-tools-v1'


def bind(raw):
    for a,b in [(previous.TOOLS,TOOLS),('pg2548-strict-current-full-seal-v1','pg2704-operation-current-full-seal-v1'),
      ('pg2544-strict-current-terminal-v1','pg2700-operation-current-terminal-v1'),
      ('pg2542-strict-current-live-binding-v1','pg2686-operation-current-live-binding-v1'),
      ('pg2552-strict-current-parent-projection-v1','pg2706-operation-current-parent-projection-v1'),
      ('pg2556-strict-owned-stage-v1','pg2712-operation-owned-stage-v1'),
      ('pg2560-strict-current-owned-post-v1','pg2716-operation-owned-post-v1'),
      ('PG2560-strict-current-owned-post-v1','PG2716-operation-owned-post-v1'),
      ('pg2554','pg2708'),('Pg2554','Pg2708'),('PG2554','PG2708'),
      ('pg2555','pg2710'),('pg2556','pg2712'),('pg2557','pg2713'),('pg2558','pg2714'),
      ('PG2512','PG2654'),('pg2512','pg2654'),(previous.SOURCE,SOURCE)]:raw=raw.replace(a,b)
    return raw


def namespace(bom=None):
    ns={**previous.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'terminal_payload':terminal_payload,'candidate_bom':candidate_bom}
    if bom is not None:
        ns['candidate_bom']=lambda:bom
        ns['terminal_payload']=lambda binding:terminal_payload(binding,bom)
    for fn in [previous.context,previous.emit_receipt,previous.emit,previous.sources]:
        exec(compile(bind(inspect.getsource(fn)),'<new actual sealed owned namespace>','exec'),ns)
    return ns


def context():return namespace()['context']()


def emit(ctx,live,state,fields,bom=None):return namespace(bom)['emit'](ctx,live,state,fields,bom)


def sources():return namespace()['sources']()
