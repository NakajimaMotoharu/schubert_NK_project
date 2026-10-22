"""Rebind all unchanged1409 raw rows; Root11 and F03 remain unaccepted."""
import inspect
import pg6896_current4213_static as previous
from pg6932_original4222_artifacts import read_whole

ROOT, W, BASE, sha = previous.ROOT, previous.W, previous.BASE, previous.sha
OLD = '2e3cdb6ff6b0b7c3af0e33413affbda6fdbb2c3f'
PRIOR = BASE / 'PG6896-current4213-static-v1/manifest.json'
PRIOR_SHA = '7870b5d870061b39f0df3b4440b1ea4688f8ceba88639322eb1dff498cfafc11'
QSHA = '7a60d8e3ebf2acad4bc4f80bf24a38ba2272c77b07e9e79f1b03ff59d083035c'
EXPECTED_RAW = EXPECTED_PAIRS = 1409


def bindings():
    scope = {**vars(previous), 'OLD': OLD, 'PRIOR': PRIOR}
    exec(compile(inspect.getsource(previous.bindings), '<current4222 unchanged binding>', 'exec'), scope)
    return scope['bindings']()


def review_changed(row):
    raise ValueError('all Main fixed; any unmatched new warning needs its own review')


def definition():
    raw = inspect.getsource(previous.definition)
    for before, after in (('PG6886-data-boundary-original-v1', 'PG6928-db-fixture-green-original-v1'),
      ('pg6886-data-boundary-original-v1', 'pg6928-db-fixture-green-original-v1'),
      ('PG6896-current4213-static-v1', 'PG6936-current4222-static-v1'),
      ('pg6896_current4213_static.py', 'pg6936_current4222_static.py')):
        raw = raw.replace(before, after)
    scope = {**vars(previous), 'OLD': OLD, 'PRIOR': PRIOR, 'PRIOR_SHA': PRIOR_SHA, 'QSHA': QSHA,
      'EXPECTED_RAW': EXPECTED_RAW, 'EXPECTED_PAIRS': EXPECTED_PAIRS, 'read_whole': read_whole,
      'bindings': bindings, 'review_changed': review_changed}
    exec(compile(raw, '<current4222 static definition>', 'exec'), scope)
    return scope['definition']()


if __name__ == '__main__':
    definition()()
