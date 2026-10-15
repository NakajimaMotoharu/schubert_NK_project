"""Real unchanged Current Chromium A01 on exactly the newly captured Root owners."""
import json
import re
from pyflakes.api import check
import pg2884_network_newcurrent_a01 as old
from pg1446_current_cold_stage import W
from pg3462_outbox_current_observer import SOURCE, BOM
from pg3466_outbox_current_live_binding import SLOT as LIVE


def code():
    live = json.loads((W / LIVE / 'manifest.safe.json').read_bytes())
    original = json.loads((W / 'pg2874-network-newcurrent-live-binding-v1/manifest.safe.json').read_bytes())
    if live['actualExit'] != 0 or live['productionSource'] != SOURCE:
        raise ValueError('actual new-source Root binding required before any Browser operation')
    # The historical successful producer is template data only. Its complete
    # actual guard is rebound to the new independently captured generation.
    raw = old.code()
    for a, b in [('PG2884', 'PG3482'), ('pg2884', 'pg3482'), ('pg2862', 'pg3462'),
                 ('pg2882-network-chr-socks-v1', 'pg3480-outbox-chr-socks-v1'),
                 (old.SOURCE, SOURCE), (old.BOM, BOM), ('PG2802', 'PG3420'),
                 ('pg2872-network-newcurrent-noargs-once-v2', 'pg3464-outbox-current-noargs-once-v1'),
                 ('pg2860-network-cold-publication-independent-post-v1', 'pg3458-current-outbox-publication-independent-post-v1')]:
        if a not in raw:
            raise ValueError('complete actual A01 source/owner boundary: ' + a)
        raw = raw.replace(a, b)
    for key in ['run', 'activation', 'cutoff', 'invocation']:
        raw = raw.replace(str(original['binding'][key]), str(live['binding'][key]))
    for a, b in [(str(original['rootPid']), str(live['rootPid'])),
                 (str(original['binding']['start']), str(live['binding']['start'])),
                 (str(original['binding']['job']), str(live['binding']['job']))]:
        raw = re.sub(r'\b' + re.escape(a) + r'\b', b, raw)
    if check(raw, '<whole actual current4856 A01 producer/consumer>'):
        raise ValueError('complete Browser producer/consumer exports required')
    compile(raw, '<real same-parent current4856 A01>', 'exec')
    return raw


if __name__ == '__main__':
    ns = {'__file__': __file__, '__name__': 'outbox_current_a01'}
    exec(compile(code(), '<new actual A01 entry>', 'exec'), ns)
    ns['main']()
