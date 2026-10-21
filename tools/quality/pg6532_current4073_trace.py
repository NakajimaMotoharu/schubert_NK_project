"""Refresh existing943 only from original4073; historical941/17/formal/cost fields immutable."""
import argparse
import inspect
import pg6258_current4034_trace as prior
from pg6528_current4073_static_join import SOURCE, read_qualified

ROOT, PMO, NAMES, W, BASE = prior.ROOT, prior.PMO, prior.NAMES, prior.W, prior.BASE
OUT = W/'pg6532-current4073-trace-v1'
PUBLIC = BASE/'PG6532-current4073-host-measurement-v1'
require, sha, trace, audit = prior.require, prior.sha, prior.trace, prior.audit
base = prior.base


def definitions(qsha, csha):
    scope = {**vars(prior), 'SOURCE': SOURCE, 'OUT': OUT, 'PUBLIC': PUBLIC,
             'read_qualified': read_qualified, 'candidates': candidates}
    raw = inspect.getsource(prior.definitions)
    for before, after in (('PG6244-six-v1', 'PG6524-six-v1'), ('4034', '4073'),
                          ('suites=606', 'suites=614'),
                          ('PG6258-current943-trace-v1', 'PG6532-current943-trace-v1')):
        raw = raw.replace(before, after)
    exec(compile(raw, '<original4073 trace definitions>', 'exec'), scope)
    return scope['definitions'](qsha, csha)


def authenticated():
    qp, _ = read_qualified()
    return definitions(sha(qp.read_bytes()), sha(qp.with_name('cases.json').read_bytes()))


def measurement(): return authenticated()['measurement']()


def candidates(texts, before_head):
    scope = {**vars(prior), 'SOURCE': SOURCE, 'OUT': OUT, 'PUBLIC': PUBLIC,
             'measurement': measurement}
    raw = inspect.getsource(prior.candidates)
    raw = raw.replace('870010d6681d74519237be7a7ca6381a190f471a',
                      'e45cfd31c8d610922f4e9432cc1cf11fa9b48338').replace('4034', '4073')
    exec(compile(raw, '<saved943 current4073 refresh>', 'exec'), scope)
    return scope['candidates'](texts, before_head)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=['publish', 'stage', 'apply', 'report'])
    args = parser.parse_args(); authenticated()[args.action]()
