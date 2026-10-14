"""Read-only fresh candidate Root/job identity; explicitly rejects historical activations."""
import inspect
import pg2450_question_current_live_binding as previous
from pg2516_current_strict_candidate_sources import SOURCE
from pg2532_strict_normal_publication_sources import candidate_bom

SLOT = 'pg2542-strict-current-live-binding-v1'


def body():
    raw = previous.body().replace('PG2428', 'PG2512')
    marker = "require(fields[1]!='91f5484b-9702-4c7c-97f3-dd5110a853f9'and fields[3]!='e1429ac8-f3dd-4e8c-83d2-1926c4ba8440')"
    if raw.count(marker) != 1:
        raise ValueError('one explicit prior-generation guard required')
    return raw.replace(marker, marker + "\nrequire(fields[1]!='06236d14-a6f8-4d05-a6ff-49c713cc2647'and fields[3]!='c347b14a-2e59-41e6-993c-a07e537cbd00')")


def entry():
    raw = inspect.getsource(previous.prior.prior.transport.main).replace(
        'pg2015-completed-run-fresh-resume-once-v1', 'pg2540-strict-current-noargs-once-v1')
    ns = {**previous.prior.prior.transport.__dict__, 'SOURCE':SOURCE, 'BOM':candidate_bom(),
          'SLOT':SLOT, 'body':body}
    exec(compile(raw, '<new current read-only actual job binding transport>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
