"""One fresh candidate ordinary noargs admission; old Source/native retained, not applied."""
import inspect
import pg2448_question_current_noargs_once as previous
from pg2538_strict_current_observer import namespace
from pg2532_strict_normal_publication_sources import candidate_bom
from pg2516_current_strict_candidate_sources import SOURCE
from pg2536_strict_normal_publication_post import payload as full_post

SLOT = 'pg2540-strict-current-noargs-once-v1'


def body(bom=None):
    if bom is None:
        bom = candidate_bom()
    if type(bom) is not str or len(bom) != 64 or set(bom) - set('0123456789abcdef'):
        raise ValueError('one immutable current candidate BOM required')
    raw = previous.body()
    for before, after in [('pg2446', 'pg2538'), (previous.SLOT, SLOT),
                          (previous.SOURCE, SOURCE), (previous.BOM, bom), ('PG2428', 'PG2512'),
                          ('require(len(records)==16)', 'require(len(records)==22)')]:
        if before not in raw:
            raise ValueError('exact ordinary-once source boundary required')
        raw = raw.replace(before, after)
    return raw


def payload(hashes):
    raw = inspect.getsource(previous.prior.payload).replace(
        'pg2174-normal-publication-full-post-v1', 'pg2536-strict-normal-publication-post-v1')
    ns = {**previous.prior.__dict__, 'full_post':full_post, 'body':body}
    exec(compile(raw, '<new current full admission projection>', 'exec'), ns)
    return ns['payload'](hashes)


def main():
    bom = candidate_bom()
    raw = inspect.getsource(previous.prior.main)
    for before, after in [('pg2176', 'pg2538'),
                          ('pg2174-normal-publication-full-post-v1', 'pg2536-strict-normal-publication-post-v1')]:
        raw = raw.replace(before, after)
    ns = {**previous.prior.__dict__, 'namespace':namespace, 'SOURCE':SOURCE, 'BOM':bom,
          'SLOT':SLOT, 'payload':payload}
    exec(compile(raw, '<new ordinary once admission entry>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
