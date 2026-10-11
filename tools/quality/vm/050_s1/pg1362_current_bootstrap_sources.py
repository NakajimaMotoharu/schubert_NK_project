"""Explicit64MiB observation only; all current SHA/security/fullrow conditions unchanged."""
from pg1356_current_bootstrap_sources import files as previous,SOURCE,BEFORE,W

LIMIT = 67108864

def files(baseline_sha):
    result = {}
    for name,raw in previous(baseline_sha).items():
        name=name.replace('1356','1362')
        raw=raw.replace('Pg1356','Pg1362').replace('pg1356','pg1362').replace('PG1356','PG1362')
        if name=='pg1362_bootstrap_existing.py':
            old='strict(baseline_path,0o600,33554432)'
            if raw.count(old)!=1:raise ValueError('one fixed baseline bound required')
            raw=raw.replace(old,'strict(baseline_path,0o600,67108864)')
            old="query+'commit;']).splitlines()"
            if raw.count(old)!=1:raise ValueError('one full24 SQL observation bound required')
            raw=raw.replace(old,"query+'commit;'],67108864).splitlines()")
        result[name]=raw
    return result
