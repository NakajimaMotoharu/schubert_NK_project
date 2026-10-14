"""Read-only actual new stopped generation Backup content; no Backup replay."""
import inspect
import json
import types
import pg2566_strict_current_backup_content as previous
import pg2716_operation_owned_post as current
from pg1446_current_cold_stage import W
from pg2674_operation_publication_sources import production

SLOT='pg2724-operation-backup-content-v1'


def payload(seals):
    live=json.loads((W/'pg2686-operation-current-live-binding-v1/manifest.safe.json').read_bytes())
    if type(live.get('actualExit'))is not int or live['actualExit']!=0 or live.get('productionSource')!=production():raise ValueError('actual new run Backup oracle required')
    raw=inspect.getsource(previous.payload)
    for a,b in [('b29fb3e5-2c46-4eac-b8f3-d03b986338e3',live['binding']['run']),
      ('2026-10-14T00:36:06.976135Z',live['binding']['cutoff']),
      ('0.1.0-PG2512/config/templates/api.yml','0.1.0-PG2654/config/templates/api.yml'),
      ('PG2560-strict-current-owned-post-v1','PG2716-operation-owned-post-v1'),
      ('PG2566-strict-current-backup-content-v1','PG2724-operation-backup-content-v1')]:raw=raw.replace(a,b)
    ns={**previous.__dict__,'SLOT':SLOT,'current':current}
    exec(compile(raw,'<actual new run independent Backup oracle>','exec'),ns);return ns['payload'](seals)


def entry():
    fn=current.entry()
    return types.FunctionType(fn.__code__,{**fn.__globals__,'SLOT':SLOT,'payload':payload},'operation_current_backup_content')


if __name__=='__main__':raise SystemExit(entry()())
