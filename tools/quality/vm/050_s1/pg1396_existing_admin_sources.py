"""Current769 existing ADMIN with fresh qualified role baseline; old failed tools unchanged."""
from pg1362_current_bootstrap_sources import files as previous,SOURCE,W

BEFORE='pg1395-existing-role-normal-post-v1'

def files(baseline_sha):
    result={}
    for name,raw in previous(baseline_sha).items():
        name=name.replace('1362','1396');raw=raw.replace('Pg1362','Pg1396').replace('pg1362','pg1396').replace('PG1362','PG1396')
        raw=raw.replace('pg1344-current-bootstrap-before-v1',BEFORE)
        result[name]=raw
    return result
