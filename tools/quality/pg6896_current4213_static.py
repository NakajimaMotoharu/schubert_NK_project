"""All unchanged1409 actual raw rows rebound; Root11 not reviewed/accepted."""
import inspect
import pg6868_current4209_static_join as prior
from pg6892_original4213_artifacts import read_whole

ROOT, W, BASE, sha = prior.ROOT, prior.W, prior.BASE, prior.sha
OLD = '2b2e4f70746bd1e1e405e18427dfd45616f51623'
PRIOR = BASE / 'PG6868-current4209-static-join-v1/manifest.json'
PRIOR_SHA = '8eb04d47ce8b39850d6368c9179dab3d6cd5a89b00b12bdd8155f43f9305ef32'
QSHA = '2814d78fe5ee54672c9a40a6aeaac151a125a75d3a68a4e48ab94390decaac78'
EXPECTED_RAW = EXPECTED_PAIRS = 1409


def bindings():
    raw = inspect.getsource(prior.bindings)
    scope = {**vars(prior), 'OLD': OLD, 'PRIOR': PRIOR}
    exec(compile(raw, '<unchanged4213 binding>', 'exec'), scope)
    return scope['bindings']()


def review_changed(row):
    raise ValueError('all Main bytes fixed; any new diagnostic requires its own PG review')


def definition():
    raw = inspect.getsource(prior.base.main)
    for before, after in (('PG6712-broker-parent-qualification-v3', 'PG6886-data-boundary-original-v1'),
        ('pg6712-broker-parent-qualification-v3', 'pg6886-data-boundary-original-v1'),
        ('PG6716-current4184-static-join-v1', 'PG6896-current4213-static-v1'),
        ('pg6716_current4184_static_join.py', 'pg6896_current4213_static.py'), ('all8511667', 'all8511669')):
        raw = raw.replace(before, after)
    scope = {**vars(prior.base), 'OLD': OLD, 'PRIOR': PRIOR, 'PRIOR_SHA': PRIOR_SHA, 'QSHA': QSHA,
      'EXPECTED_RAW': EXPECTED_RAW, 'EXPECTED_PAIRS': EXPECTED_PAIRS, 'read_whole': read_whole,
      'bindings': bindings, 'review_changed': review_changed}
    exec(compile(raw, '<unchanged4213 all1409>', 'exec'), scope)
    return scope['main']


if __name__ == '__main__':
    definition()()
