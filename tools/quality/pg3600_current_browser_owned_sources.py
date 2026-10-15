"""New-only current Browser terminal/composite/parent18 bound normal owned-stop graph."""
import inspect
import pg3490_outbox_owned_sources as original
import pg3520_outbox_owned_sources_v2 as successful
import pg3582_current_browser_acceptance as acceptance
import pg3650_current_browser_composite_seal_v2 as composite

SOURCE=acceptance.SOURCE
BOM=acceptance.BOM
TOOLS='pg3600-current-browser-owned-stop-tools-v1'


class Current:
    SOURCE=SOURCE
    BOM=BOM
    SEAL=composite.SLOT
    TERM=acceptance.TERM
    terminal_payload=staticmethod(acceptance.terminal_payload)
    seal_payload=staticmethod(composite.payload)


current=Current


def final_bind(raw):
    raw=successful.final_bind(raw)
    for old,new in [(successful.TOOLS,TOOLS),('pg3476-outbox-current-full-seal-v1',composite.SLOT),
                    ('pg3472-outbox-current-terminal-v1',acceptance.TERM),
                    ('pg3466-outbox-current-live-binding-v1',acceptance.LIVE),
                    ('pg3478-outbox-parent-projection-v1','pg3594-current-browser-parent-projection-v1'),
                    ('pg3524-outbox-owned-stage-v2','pg3604-current-browser-owned-stage-v1'),
                    ('pg3526-outbox-owned-post-v2','pg3606-current-browser-owned-post-v1'),
                    ('PG3526-outbox-owned-post-v2','PG3606-current-browser-owned-post-v1'),
                    ('pg3520','pg3600'),('Pg3520','Pg3600'),('PG3520','PG3600'),
                    ('pg3522','pg3602'),('pg3524','pg3604'),('pg3525','pg3605'),('pg3527','pg3607')]:raw=raw.replace(old,new)
    return raw


def bind(raw):return final_bind(original.bind(raw))


def candidate_bom():return BOM


def namespace():
    ns={**original.__dict__,'TOOLS':TOOLS,'bind':bind,'current':current}
    exec(compile(inspect.getsource(original.namespace),'<new current Browser complete owned graph composer>','exec'),ns)
    return ns['namespace']()


def context():return namespace()['context']()


def sources():
    values={final_bind(n):final_bind(raw)for n,raw in namespace()['sources']().items()}
    for name,raw in values.items():
        if any(old in raw for old in ['b2d6f605','pg2654','PG2654','pg3490','Pg3490','pg3520','Pg3520']):
            raise ValueError('legacy positive role in final Browser owned '+name)
    return values
