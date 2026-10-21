"""Current4056 XML/source join only; held source11 and missing semantics12 are not promoted."""
import inspect
import pg6282_current4040_static_join as prior
from pg6456_current4056_trace import SOURCE, read_qualified
from pg6458_current4056_static_plan import PRIOR, PRIOR_SHA, OLD

INPUT = prior.BASE/'PG6460-normal-publication-static-review-v1/manifest.json'
INPUT_SHA = 'edbca132babc30692228491bd45fbff6abea406702782418377182fb88ceb7b4'


def definitions():
    scope = {**vars(prior), 'SOURCE': SOURCE, 'read_qualified': read_qualified,
        'PRIOR': PRIOR, 'PRIOR_SHA': PRIOR_SHA, 'OLD': OLD, 'INPUT': INPUT, 'INPUT_SHA': INPUT_SHA}
    raw = inspect.getsource(prior.main)
    for before, after in (
        ('4040', '4056'), ('1350', '1361'), ('PG6272', 'PG6452'),
        ('PG6268-outbox-failure-qualification-v1', 'PG6450-morning-sequence-qualification-v1'),
        ('pg6268-outbox-failure-qualification-v1', 'pg6450-morning-sequence-qualification-v1'),
        ('d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225', '8eb15b608718eb0f9eac4a92ccd03db4882a5436876d13c66563beedc3daf3c0'),
        ('pg6266-outbox-failure-selected-v1', 'pg6448-morning-sequence-green-v1'),
        ('PG6282-current4056-static-join-v1', 'PG6462-current4056-static-join-v1')):
        if before not in raw:
            raise ValueError('exact current4056 semantic binding '+before)
        raw = raw.replace(before, after)
    exec(compile(raw, '<actual4056 semantic references>', 'exec'), scope)
    return scope


def main(): return definitions()['main']()


if __name__ == '__main__':
    main()
