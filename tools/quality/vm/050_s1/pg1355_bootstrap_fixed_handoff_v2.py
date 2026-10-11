"""New-only canonical owner metadata; original proof/seals and all nine values unchanged."""
import pg1353_bootstrap_fixed_handoff as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE

def payload(seals):
    raw = previous.payload(seals)
    old = 'locks[name]=metadata9(st)'
    if raw.count(old) != 1:
        raise ValueError('one owner metadata boundary required')
    raw = raw.replace(old, 'locks[name]=list(metadata9(st))')
    raw = raw.replace('pg1353-bootstrap-fixed-handoff-v1', 'pg1355-bootstrap-fixed-handoff-v2').replace('PG1353', 'PG1355')
    compile(raw, '<canonical actual owner handoff>', 'exec')
    return raw

def source():
    return previous.source().replace('pg1353-bootstrap-fixed-handoff-v1', 'pg1355-bootstrap-fixed-handoff-v2')

def main():
    env = dict(previous.prior.previous.prior.prior.previous.transport.__dict__, SOURCE=SOURCE, payload=payload)
    exec(compile(source(), '<canonical fixed owner handoff>', 'exec'), env)
    return env['main']()

if __name__ == '__main__':
    raise SystemExit(main())
