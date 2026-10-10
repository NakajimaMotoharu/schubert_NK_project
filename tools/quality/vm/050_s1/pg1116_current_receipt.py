"""Bind SSC253's actual new parent to the existing independent PID1/DONE oracle.

Receipt-only qualification: original/source/inventory/owned-stop remain separate.
No VM operations, source-result reuse, or production expected-value generation.
"""
import datetime
import uuid
from pathlib import Path

FIELDS = {'boot', 'invocation', 'job', 'start', 'run', 'cutoff', 'activation'}
CURRENT = {
    'boot': 'cbca87383b244090b77cbf029677cdd6',
    'invocation': '21f20c0cdbe34ce99431a55b10f92285',
    'job': '36002',
    'start': 34658346852,
}


def qualify(binding, rows, done):
    if type(binding) is not dict or set(binding) != FIELDS:
        raise ValueError('current receipt binding refused')
    if any(type(binding[k]) is not type(v) or binding[k] != v
           for k, v in CURRENT.items()):
        raise ValueError('current parent generation refused')
    for key in ('run', 'activation'):
        value = binding[key]
        if type(value) is not str:
            raise ValueError('current original identifier refused')
        parsed = uuid.UUID(value)
        if parsed.version != 4 or str(parsed) != value:
            raise ValueError('current original identifier refused')
    cutoff = binding['cutoff']
    if type(cutoff) is not str or not cutoff.endswith('Z'):
        raise ValueError('current cutoff refused')
    stamp = datetime.datetime.fromisoformat(cutoff.replace('Z', '+00:00'))
    lower = datetime.datetime(2026, 10, 10, 12, 40, 25, tzinfo=datetime.timezone.utc)
    if not lower <= stamp <= lower + datetime.timedelta(minutes=30):
        raise ValueError('current cutoff interval refused')
    # Read the pre-existing independent byte/journal oracle unchanged. Binding
    # is actual captured original data, never old successful cohort constants.
    env = {'__name__': 'current_parent_receipt'}
    oracle = Path(__file__).with_name('pg609_parent_receipt.py').read_bytes()
    exec(compile(oracle, '<independent PID1/DONE oracle>', 'exec'), env)
    env.update(BOOT=binding['boot'], INV=binding['invocation'], JOB=binding['job'],
               START=binding['start'], RUN=binding['run'], CUTOFF=cutoff,
               ACT=binding['activation'])
    return env['completed'](rows, done)
