"""Actual4054 semantic join; fresh context-only decisions and unresolved12 remain explicit."""
import inspect
import pg6282_current4040_static_join as prior
from pg6420_current4054_trace import SOURCE, read_qualified
from pg6418_current4054_static_plan import PRIOR, PRIOR_SHA, OLD

INPUT = prior.BASE/'PG6428-backup-normal-static-review-v1/manifest.json'
INPUT_SHA = '2da516f19954d662b9cec1d2db70cbc0a1a8c0d7b31f09da22737158102f42bf'


def definitions():
    scope = {**vars(prior), 'SOURCE': SOURCE, 'read_qualified': read_qualified,
             'PRIOR': PRIOR, 'PRIOR_SHA': PRIOR_SHA, 'OLD': OLD, 'INPUT': INPUT, 'INPUT_SHA': INPUT_SHA}
    raw = inspect.getsource(prior.main)
    for before, after in (
        ('4040', '4054'), ('1350', '1358'), ('PG6272', 'PG6408'),
        ('PG6268-outbox-failure-qualification-v1', 'PG6414-web-frame-pending-qualification-v1'),
        ('pg6268-outbox-failure-qualification-v1', 'pg6414-web-frame-pending-qualification-v1'),
        ('d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225', 'f214986209f003c92248644f55e617042af273ab6b652a2e753dffceda30498f'),
        ('pg6266-outbox-failure-selected-v1', 'pg6412-web-frame-pending-selected-v1'),
        ('PG6282-current4054-static-join-v1', 'PG6424-current4054-static-join-v1')):
        if before not in raw:
            raise ValueError('exact source/whole semantic binding '+before)
        raw = raw.replace(before, after)
    exec(compile(raw, '<actual4054 semantic references>', 'exec'), scope)
    return scope


def main(): return definitions()['main']()


if __name__ == '__main__':
    main()
