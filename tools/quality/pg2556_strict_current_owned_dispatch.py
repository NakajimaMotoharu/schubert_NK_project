"""Single authenticated fresh owned stop after genuine terminal/whole/parent18."""
import json
import types
import pg2460_question_current_owned_dispatch as previous
from pg2554_strict_current_owned_sources import sources, context, SOURCE, TOOLS
from pg2532_strict_normal_publication_sources import candidate_bom
from pg2548_strict_current_full_seal import payload
from pg1446_current_cold_stage import W

GUEST = '/var/lib/pgpt-s1-preservation/' + TOOLS
REMOTE = '/home/ubuntu/pg2556-strict-owned-stage-v1'
ARCHIVE = 'pg2556-' + TOOLS + '.tar'
POST_SLOT = 'pg2548-strict-current-full-seal-v1'


def stage():
    raw = previous.STAGE
    for before, after in [(previous.ARCHIVE, ARCHIVE), (previous.REMOTE, REMOTE), (previous.TOOLS, TOOLS),
        ('pg2458', 'pg2554'), ('Pg2458', 'Pg2554'), ('pg2460', 'pg2556'), ('PG2460', 'PG2556'),
        ('PG2428', 'PG2512'), (previous.SOURCE, SOURCE), (previous.BOM, candidate_bom())]:
        raw = raw.replace(before, after)
    return raw


def post_payload():
    live = json.loads((W / 'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
    if type(live.get('actualExit')) is not int or live['actualExit'] != 0 or live.get('productionSource') != SOURCE:
        raise ValueError('actual fresh current Source binding required')
    return payload({**live['binding'], 'rootPid':live['rootPid']})


def run_source():
    raw = previous.run_source()
    for before, after in [('pg2460', 'pg2556'), ('pg2459', 'pg2555'), ('pg2461', 'pg2557'),
                          ('pg2462', 'pg2558'), ('Pg2458', 'Pg2554'), ('PG2428', 'PG2512')]:
        raw = raw.replace(before, after)
    return raw


def run_action(action):
    base = previous.prior.previous.prior.prior.prior.prior.runner
    ns = {**base.__dict__, 'GUEST':GUEST, 'REMOTE':REMOTE, 'ARCHIVE':ARCHIVE, 'STAGE':stage(),
          'PARENT_PREQUAL':previous.PARENT_PREQUAL.replace('pg2458', 'pg2554'), 'sources':sources,
          'context':context, 'SOURCE':SOURCE, 'TOOLS':TOOLS, 'BOM':candidate_bom(),
          'POST_SLOT':POST_SLOT, 'post_payload':post_payload}
    exec(compile(run_source(), '<fresh new owned-stop entry>', 'exec'), ns)
    return ns['run_action'](action)


def main():
    base = previous.prior.previous.prior.prior.prior.prior
    return types.FunctionType(base.main.__code__, {**base.__dict__, 'run_action':run_action})()


if __name__ == '__main__':
    raise SystemExit(main())
