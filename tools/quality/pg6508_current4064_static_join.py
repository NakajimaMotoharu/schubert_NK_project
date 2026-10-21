"""Authenticate current4064 XML refs for1338+12; held11 remain unreviewed, no native authority."""
import inspect
import pg6282_current4040_static_join as prior
from pg6506_current4064_trace import SOURCE, read_qualified
from pg6502_web_current_static_plan import PRIOR, PRIOR_SHA, OLD

INPUT = prior.BASE/'PG6504-web-owned-semantic-review-v1/manifest.json'
INPUT_SHA = '383b7aa7279403ab60127a47ef96738049ebb1ae6db0e40b326b121369ebfc15'


def definitions():
    scope = {**vars(prior), 'SOURCE': SOURCE, 'read_qualified': read_qualified,
        'PRIOR': PRIOR, 'PRIOR_SHA': PRIOR_SHA, 'OLD': OLD, 'INPUT': INPUT, 'INPUT_SHA': INPUT_SHA}
    raw = inspect.getsource(prior.main)
    for before, after in (
        ('4040', '4064'), ('1350', '1361'), ('PG6272', 'PG6490'),
        ('PG6268-outbox-failure-qualification-v1', 'PG6500-web-owned-component-qualification-v5'),
        ('pg6268-outbox-failure-qualification-v1', 'pg6500-web-owned-component-qualification-v5'),
        ('d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225', '67be969bc999b8cc5cd020faea6f1604bf8c32ebf8673f6db4a13910a8e90722'),
        ('pg6266-outbox-failure-selected-v1', 'pg6498-web-owned-component-v5'),
        ('PG6282-current4064-static-join-v1', 'PG6508-current4064-static-join-v1')):
        if before not in raw:
            raise ValueError('exact current4064 semantic binding '+before)
        raw = raw.replace(before, after)
    exec(compile(raw, '<actual4064 semantic references>', 'exec'), scope)
    return scope


def main(): return definitions()['main']()


if __name__ == '__main__': main()
