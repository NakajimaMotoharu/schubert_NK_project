"""One exact-entry retire/reload in fresh normal scopes; no Root or business start."""
import json
import os
import sys
import pg3010_current_resume_owned_dispatch as previous
from pg3034_current_runtime_retirement_sources import sources, SOURCE, SHA, TOOLS
from pg3012_current_resume_owned_post import payload as stopped_payload
from pg1446_current_cold_stage import W, P
from pg1674_critical_management_gate import management_gate
import pg1257_fresh_independent_terminal_post as schema

GUEST = '/var/lib/pgpt-s1-preservation/' + TOOLS
REMOTE = '/home/ubuntu/pg3038-fixed-stage-v1'
ARCHIVE = 'pg3038-' + TOOLS + '.tar'
POST_SLOT = 'pg3012-current-resume-owned-post-v1'
STAGE = previous.stage().replace(previous.ARCHIVE, ARCHIVE).replace(previous.REMOTE, REMOTE).replace(previous.TOOLS, TOOLS).replace('pg3006', 'pg3034').replace('Pg3006', 'Pg3034').replace('pg3010', 'pg3038').replace('PG3010', 'PG3038')
PARENT_PREQUAL = previous.namespace()['previous'].PARENT_PREQUAL.replace('pg2458', 'pg3034')


def context():
    p = json.loads((W / POST_SLOT / 'manifest.safe.json').read_bytes())
    if not (p['actualExit'] == 0 and p['productionSource'] == SOURCE and p['allClientAdvisoryFlock0'] and p['proofHashes']['after.private.json']['sha256'] == SHA):
        raise ValueError('actual current stopped image required')
    return SHA, None, p['genuineCompletion'], None


def post_payload():
    p = json.loads((W / POST_SLOT / 'manifest.safe.json').read_bytes())
    build = json.loads((W / 'pg3008-frozen-v1.safe.json').read_bytes())
    receipt = (W / previous.TOOLS / 'pg3006_parent_receipt.py').read_text()
    seals = {n: p['proofHashes'][n]['sha256'] for n in schema.previous.SEALS}
    return 'HASHES=' + repr(build['fileHashes']) + '\nRECEIPT=' + repr(receipt) + '\n' + stopped_payload(seals)


def run_source():
    raw = previous.run_source().replace("('stage', 'stop')", "('stage', 'retire')")
    raw = raw.replace("post['privateBeforeSha256'] != before", "post['proofHashes']['after.private.json']['sha256'] != before")
    for a, b in [('pg3008', 'pg3036'), ('pg3010', 'pg3038'), ('pg3011', 'pg3039'), ('pg3013', 'pg3041'), ('Pg3006', 'Pg3034'), ('Pg3034NativeStop stop', 'Pg3034NativeStop retire')]:
        raw = raw.replace(a, b)
    return raw


def run_action(action):
    bound = previous.namespace()
    base = bound['previous'].prior.previous.prior.prior.prior.prior.runner
    ns = {**base.__dict__, 'GUEST': GUEST, 'REMOTE': REMOTE, 'ARCHIVE': ARCHIVE, 'STAGE': STAGE, 'PARENT_PREQUAL': PARENT_PREQUAL, 'sources': sources, 'context': context, 'SOURCE': SOURCE, 'TOOLS': TOOLS, 'BOM': previous.BOM, 'POST_SLOT': POST_SLOT, 'post_payload': post_payload}
    exec(compile(run_source(), '<current exact retirement action>', 'exec'), ns)
    return ns['run_action'](action)


def main():
    if sys.argv[1:] not in (['stage'], ['retire']):
        raise ValueError('distinct stage or retire only')
    os.umask(0o077)
    with management_gate(P / 'current-management-critical.lock'):
        return run_action(sys.argv[1])


if __name__ == '__main__':
    raise SystemExit(main())
