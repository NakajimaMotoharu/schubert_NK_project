"""Independent whole fresh owned-stop post; never issue lifecycle actions."""
import inspect
import json
from pyflakes.api import check
import pg2464_question_current_owned_post as previous
from pg2554_strict_current_owned_sources import context, TOOLS, SOURCE
from pg2532_strict_normal_publication_sources import candidate_bom
from pg1446_current_cold_stage import W

SLOT = 'pg2560-strict-current-owned-post-v1'


def emit(seals, ctx, live, bom=None):
    if bom is None:
        bom = candidate_bom()
    raw = previous.emit(seals, ctx, live)
    for before, after in [(previous.TOOLS, TOOLS), ('pg2458', 'pg2554'), ('Pg2458', 'Pg2554'),
        ('PG2458', 'PG2554'), (previous.SLOT, SLOT), ('PG2464-question-current-owned-post-v1', 'PG2560-strict-current-owned-post-v1'),
        ('pg2456-question-current-full-seal-v1', 'pg2548-strict-current-full-seal-v1'),
        (previous.SOURCE, SOURCE), (previous.BOM, bom), ('PG2428', 'PG2512'), ('pg2428-manifest.sig', 'pg2512-manifest.sig')]:
        raw = raw.replace(before, after)
    if check('HASHES={}\nRECEIPT="actual"\n' + raw, '<fresh stopped whole post>'):
        raise ValueError('complete new current stopped namespace required')
    compile(raw, '<fresh new owned-stop full post>', 'exec')
    return raw


def payload(seals):
    live = json.loads((W / 'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
    return emit(seals, context(), live)


def entry():
    raw = inspect.getsource(previous.prior.previous.prior.prior.prior.previous.main)
    for before, after in [('pg2038-stop-v1', 'pg2556-stop-v1'), ('pg2031-frozen-v1', 'pg2555-frozen-v1'),
        ('pg2030_parent_receipt.py', 'pg2554_parent_receipt.py'), ('pg2030-native-stop-v1', 'pg2554-native-stop-v1')]:
        raw = raw.replace(before, after)
    ns = {**previous.prior.previous.prior.prior.prior.previous.__dict__, 'SLOT':SLOT,
          'TOOLS':TOOLS, 'SOURCE':SOURCE, 'BOM':candidate_bom(), 'payload':payload}
    exec(compile(raw, '<fresh independent stopped post entry>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
