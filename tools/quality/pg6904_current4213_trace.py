"""Original4213 current943 measurement only; preserve historical and formal/cost values."""
import argparse
import inspect
import pg6872_current4209_trace as prior
from pg6892_original4213_artifacts import read_whole

ROOT, PMO, NAMES, W, BASE = prior.ROOT, prior.PMO, prior.NAMES, prior.W, prior.BASE
SOURCE = '2e3cdb6ff6b0b7c3af0e33413affbda6fdbb2c3f'
OUT = W / 'pg6904-current4213-trace-v1'
PUBLIC = BASE / 'PG6904-current4213-host-measurement-v1'
require, sha, trace, audit = prior.require, prior.sha, prior.trace, prior.audit


def read_qualified():
    qp, q, _ = read_whole()
    require(q['productionSource'] == SOURCE, 'genuine current4213 source')
    return qp, q


def definitions(qsha, csha):
    scope = {**vars(prior), 'SOURCE': SOURCE, 'OUT': OUT, 'PUBLIC': PUBLIC, 'read_qualified': read_qualified, 'candidates': candidates}
    raw = inspect.getsource(prior.definitions)
    for before, after in (('4209', '4213'), ('653', '656'), ('PG6862-six-v1', 'PG6890-six-v1'), ('PG6872-current943-trace-v1', 'PG6904-current943-trace-v1')):
        raw = raw.replace(before, after)
    exec(compile(raw, '<current4213 trace definitions>', 'exec'), scope)
    return scope['definitions'](qsha, csha)


def authenticated():
    qp, _ = read_qualified()
    return definitions(sha(qp.read_bytes()), sha(qp.with_name('cases.json').read_bytes()))


def measurement():
    return authenticated()['measurement']()


def candidates(texts, before_head):
    scope = {**vars(prior), 'SOURCE': SOURCE, 'OUT': OUT, 'PUBLIC': PUBLIC, 'measurement': measurement}
    raw = inspect.getsource(prior.candidates).replace('4c0343a55b5fe41dad766a520558363e81f01541', '2b2e4f70746bd1e1e405e18427dfd45616f51623').replace("'4209'", "'4213'")
    exec(compile(raw, '<preserve2b2e current943 history>', 'exec'), scope)
    return scope['candidates'](texts, before_head)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('publish', 'stage', 'apply', 'report'))
    authenticated()[parser.parse_args().action]()
