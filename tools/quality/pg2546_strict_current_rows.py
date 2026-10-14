"""Read-only independent all24 DB oracle bound to actual fresh admission image."""
import inspect
import types
import pg2454_question_current_rows as previous
from pg2516_current_strict_candidate_sources import SOURCE

SLOT = 'pg2546-strict-current-rows-v1'
BEFORE = 'd9b9567c29f2948d9990f464de3e895b8c0683a4020d735a5bc49c0940e4f106'


def payload():
    raw = inspect.getsource(previous.payload)
    for before, after in [('pg2450-question-current-live-binding-v1', 'pg2542-strict-current-live-binding-v1'),
                          ('pg2448-question-current-noargs-once-v1', 'pg2540-strict-current-noargs-once-v1')]:
        raw = raw.replace(before, after)
    # The factory binds BEFORE/SLOT from its complete namespace. Do not import
    # another source's successful rows or append new counts to its receipt.
    ns = {**previous.__dict__, 'BEFORE':BEFORE, 'SLOT':SLOT, 'SOURCE':SOURCE}
    ns['prior'] = types.SimpleNamespace(**previous.prior.__dict__)
    exec(compile(raw, '<fresh actual same-day DB source factory>', 'exec'), ns)
    return ns['payload']()


def entry():
    raw = inspect.getsource(previous.prior.prior.transport.main).replace(
        'pg2021-fresh-resume-terminal-receipt-v1', 'pg2544-strict-current-terminal-v1')
    ns = {**previous.prior.prior.transport.__dict__, 'SOURCE':SOURCE, 'SLOT':SLOT, 'payload':payload}
    exec(compile(raw, '<fresh all24 independent capture>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
