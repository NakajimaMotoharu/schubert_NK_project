"""One a2ecc ordinary Root, same1800s budget and ownership, prior80 data only."""
import inspect
import datetime
import json
import pg4892_new_normal_root_once as previous
import pg5014_ssc304_publication_post as post
import pg5018_new_current_same_peer_observer as observer
from pg4996_resume_connection import authenticate_host

W, P, SSH = previous.W, previous.P, previous.SSH
SLOT = 'pg5022-new-normal-root-once-v1'
SOURCE, BOM = observer.SOURCE, observer.BOM
QUALIFICATION = 'pg5034-newday-normal-root-qualification-v1'


def oracle_applicable(proof, now, before_sha):
    ns = {**vars(previous), 'SOURCE': SOURCE}
    exec(compile(inspect.getsource(previous.oracle_applicable), '<same independent applicability>', 'exec'), ns)
    return ns['oracle_applicable'](proof, now, before_sha)


def action():
    raw = observer.bind(previous.action())
    for a, b in [(previous.SLOT, SLOT), ('require(len(records)==72)', 'require(len(records)==80)')]:
        if raw.count(a) != 1:
            raise ValueError('one fresh ordinary once boundary ' + a)
        raw = raw.replace(a, b, 1)
    return raw


def payload(hashes):
    ns = {**vars(previous.previous), 'post': post, 'observer': observer, 'SLOT': SLOT,
          'SOURCE': SOURCE, 'BOM': BOM, 'action': action}
    exec(compile(inspect.getsource(previous.previous.payload), '<all80 normal Root once>', 'exec'), ns)
    return ns['payload'](hashes)


def main():
    from pg5016_new_current_readonly import context
    oracle_applicable(json.loads((W / 'pg5032-new-day-query-preflight-v1/manifest.safe.json').read_bytes()),
                      datetime.datetime.now(datetime.timezone.utc), context())
    ns = {**vars(previous.previous), 'post': post, 'observer': observer, 'SLOT': SLOT,
          'SOURCE': SOURCE, 'BOM': BOM, 'QUALIFICATION': QUALIFICATION,
          'payload': payload, 'authenticate_host': authenticate_host}
    raw = inspect.getsource(previous.previous.main)
    raw = raw.replace('pg4730-new-current-readonly-v1', 'pg5016-new-current-readonly-v1').replace('pg4734', 'pg5018')
    exec(compile(raw, '<single a2ecc normal Root entry>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
