"""Current943 only from the original4222; historical17/formal/estimates fixed."""
import argparse
import inspect
import pg6904_current4213_trace as previous
from pg6932_original4222_artifacts import read_whole

ROOT, PMO, NAMES, W, BASE = previous.ROOT, previous.PMO, previous.NAMES, previous.W, previous.BASE
SOURCE = 'e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
OUT = W / 'pg6944-current4222-trace-v1'
PUBLIC = BASE / 'PG6944-current4222-host-measurement-v1'
require, sha, trace, audit = previous.require, previous.sha, previous.trace, previous.audit


def read_qualified():
    qp, q, _ = read_whole()
    require(q['productionSource'] == SOURCE, 'genuine original4222 source')
    return qp, q


def definitions(qsha, csha):
    raw = inspect.getsource(previous.definitions)
    for before, after in (('4213', '4222'), ('656', '660'), ('PG6890-six-v1', 'PG6930-six-v1'), ('PG6904-current943-trace-v1', 'PG6944-current943-trace-v1')):
        raw = raw.replace(before, after)
    scope = {**vars(previous), 'SOURCE': SOURCE, 'OUT': OUT, 'PUBLIC': PUBLIC,
      'read_qualified': read_qualified, 'candidates': candidates}
    exec(compile(raw, '<current4222 trace definition>', 'exec'), scope)
    return scope['definitions'](qsha, csha)


def authenticated():
    qp, _ = read_qualified()
    return definitions(sha(qp.read_bytes()), sha(qp.with_name('cases.json').read_bytes()))


def measurement():
    return authenticated()['measurement']()


def candidates(texts, before_head):
    raw = inspect.getsource(previous.candidates).replace('2b2e4f70746bd1e1e405e18427dfd45616f51623', '2e3cdb6ff6b0b7c3af0e33413affbda6fdbb2c3f').replace('"\'4213\'"', '"\'4222\'"')
    scope = {**vars(previous), 'SOURCE': SOURCE, 'OUT': OUT, 'PUBLIC': PUBLIC, 'measurement': measurement}
    exec(compile(raw, '<preserve2e3c943 history>', 'exec'), scope)
    return scope['candidates'](texts, before_head)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('publish', 'stage', 'apply', 'report'))
    authenticated()[parser.parse_args().action]()
