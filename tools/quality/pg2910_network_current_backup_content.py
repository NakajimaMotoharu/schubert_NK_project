"""Read-only current a9/79a Backup content, no Root/Backup/restore replay."""
import inspect
import json
import types
import pg2566_strict_current_backup_content as previous
import pg2898_network_owned_post as current
from pg1446_current_cold_stage import W
from pg2890_network_owned_sources import SOURCE

SLOT='pg2910-network-current-backup-content-v1'


def payload(seals):
    live=json.loads((W/'pg2874-network-newcurrent-live-binding-v1/manifest.safe.json').read_bytes())
    if type(live.get('actualExit'))is not int or live['actualExit']!=0 or live.get('productionSource')!=SOURCE:
        raise ValueError('actual current run Backup oracle required')
    raw=inspect.getsource(previous.payload)
    for a,b in [('b29fb3e5-2c46-4eac-b8f3-d03b986338e3',live['binding']['run']),
        ('2026-10-14T00:36:06.976135Z',live['binding']['cutoff']),
        ('0.1.0-PG2512/config/templates/api.yml','0.1.0-PG2802/config/templates/api.yml'),
        ('PG2560-strict-current-owned-post-v1','PG2898-network-owned-post-v1'),
        ('PG2566-strict-current-backup-content-v1','PG2910-network-current-backup-content-v1')]:
        if a not in raw:raise ValueError('one actual oracle binding role required')
        raw=raw.replace(a,b)
    ns={**previous.__dict__,'SLOT':SLOT,'current':current}
    exec(compile(raw,'<current actual independent Backup content>','exec'),ns)
    return ns['payload'](seals)


def entry():
    fn=current.entry()
    return types.FunctionType(fn.__code__,{**fn.__globals__,'SLOT':SLOT,'payload':payload},'network_current_backup_content')


if __name__=='__main__':raise SystemExit(entry()())
