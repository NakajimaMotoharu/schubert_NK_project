"""Exact canonical-runtime UNKNOWN owner handoff; never replay configuration."""
import ast
from pg1165_runtime_failed_owner_handoff import source as previous


def source():
    s = previous()
    changes = [
        ('from pg1164_runtime_failed_owner_proof import payload as previous', 'from pg1177_canonical_runtime_owner_proof import payload as previous'),
        ('pg1164-runtime-failed-owner-proof-v1.safe.json', 'pg1177-canonical-runtime-owner-proof-v1.safe.json'),
        ('8f0794b3466ea22bbff455b907788ed7976a3c4869b2ed7b7452a84acdc971d5', '2c8328ea21f976d3ae914ef584a8a6454f56f73568a90ff3191f38299e40fc1f'),
        ('runtime-failed-owner-proof-v1', 'canonical-runtime-owner-proof-v1'),
        ('runtime-failed-owner-handoff-v1', 'canonical-runtime-owner-handoff-v1'),
        ('415524', '420139'), ('4807423', '5003981'),
        ('415553', '420168'), ('4807540', '5004100'),
        ('dff614fe6734a813f68a6c816bce48da90749373d222093c8a952d30b8764e5a', 'fa4551d834910cac50c0292d04405b0ec512dc984079969a50ccc3f9c2fb1f8b'),
        ('pg1165-canonical-runtime-owner-handoff-v1', 'pg1178-canonical-runtime-owner-handoff-v1'),
        ('PG1165-canonical-runtime-owner-handoff-v1', 'PG1178-canonical-runtime-owner-handoff-v1'),
    ]
    for old, new in changes:
        if old not in s:
            raise ValueError('fixed canonical owner binding refused')
        s = s.replace(old, new)
    ast.parse(s)
    return s


if __name__ == '__main__':
    exec(compile(source(), '<canonical owner once handoff>', 'exec'),
         {'__name__': '__main__', '__file__': __file__})
