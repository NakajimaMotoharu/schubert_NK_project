"""Fresh old-deployment full11/native46 authentication; data only, no new runtime authority."""
import hashlib
import inspect
import json
import pg3752_current_preservation_readonly as previous
from pg3976_literal_invariant_signed_candidate import OLD_SOURCE as CURRENT, OLD_BOM as BOM

SLOT = 'pg3978-current-preservation-readonly-v1'
AFTER = '/var/lib/pgpt-s1-preservation/pg3902-native-stop-v1/after.private.json'
AFTER_SHA = '45487171cb66fd63543092c276247684833e1d334eb58d8e701ecec67cd2a2a2'


def payload():
    post = json.loads((previous.W / 'pg3908-current-runtime-retirement-post-v1/manifest.safe.json').read_bytes())
    if not (post['actualExit'] == 0 and post['productionSource'] == CURRENT and post['proofHashes']['after.private.json']['sha256'] == AFTER_SHA and post['nativePhysicalFiles'] == 46):
        raise ValueError('actual completed current retirement full11/native46 first')
    raw = previous.payload()
    changes = {'/var/lib/pgpt-s1-preservation/pg3662-native-stop-v1/after.private.json': AFTER,
               "base/'pg3662-native-stop-v1/after.private.json'": "base/'pg3902-native-stop-v1/after.private.json'",
               previous.CURRENT: CURRENT, previous.BOM: BOM, 'PG3420': 'PG3748', 'pg3420': 'pg3748',
               "==34)": "==46)", 'native34Preserved': 'native46Preserved'}
    # The original sealed hash is a standalone assignment; its value is immutable data.
    old_hash = json.loads((previous.W / 'pg3668-current-browser-runtime-retirement-post-v1/manifest.safe.json').read_bytes())['proofHashes']['after.private.json']['sha256']
    changes[old_hash] = AFTER_SHA
    for old, new in changes.items(): raw = raw.replace(old, new)
    if raw.count(AFTER_SHA) != 1 or "==46)" not in raw or 'native34Preserved' in raw or "base/'pg3902-native-stop-v1/after.private.json'" not in raw:
        raise ValueError('exact latest full11/native46 read-only binding')
    compile(raw, '<fresh current full11/native46 reader>', 'exec')
    return raw


def main():
    values = {**previous.__dict__, 'CURRENT': CURRENT, 'BOM': BOM, 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(previous.main), '<fresh current existing VM and preserved data>', 'exec'), values)
    return values['main']()


if __name__ == '__main__': raise SystemExit(main())
