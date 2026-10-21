"""Join only actual original4052 cases; source-only review is never a PASS substitute."""
import inspect
import pg6282_current4040_static_join as prior
from pg6390_current4052_trace import SOURCE, read_qualified
from pg6392_current4052_static_plan import PRIOR, PRIOR_SHA, OLD

INPUT = prior.BASE/'PG6404-runtime-boundary-static-review-v1/manifest.json'
INPUT_SHA = '5c32e4d5d2203baabfabc5a590439a7a22c2fbdedb6478de0effff48c1633ea9'


def definitions():
    scope = {**vars(prior), 'SOURCE': SOURCE, 'read_qualified': read_qualified,
             'PRIOR': PRIOR, 'PRIOR_SHA': PRIOR_SHA, 'OLD': OLD, 'INPUT': INPUT, 'INPUT_SHA': INPUT_SHA}
    raw = inspect.getsource(prior.main)
    for before, after in (
        ('4040', '4052'), ('1350', '1355'), ('PG6272', 'PG6386'),
        ('PG6268-outbox-failure-qualification-v1', 'PG6384-web-fatal-callback-retry-qualification-v1'),
        ('pg6268-outbox-failure-qualification-v1', 'pg6384-web-fatal-callback-retry-qualification-v1'),
        ('d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225', '7896c2a6d7d650cf2a67f9270e0ad039360c7a5ba073cf84685adddc578295f7'),
        ('pg6266-outbox-failure-selected-v1', 'pg6382-web-fatal-callback-retry-v1'),
        ('PG6282-current4052-static-join-v1', 'PG6406-current4052-static-join-v1')):
        if before not in raw:
            raise ValueError('exact current source/whole semantic binding '+before)
        raw = raw.replace(before, after)
    exec(compile(raw, '<actual4052 semantic references>', 'exec'), scope)
    return scope


def main(): return definitions()['main']()


if __name__ == '__main__':
    main()
