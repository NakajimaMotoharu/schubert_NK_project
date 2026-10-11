"""New-only explicit SQL word-boundary, not old owner hotpatch or oracle relaxation."""
import pg1374_bootstrap_role_sources_v2 as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE,W

def files():
    result={}
    for name,raw in previous.files().items():
        name=name.replace('1374','1380');raw=raw.replace('Pg1374','Pg1380').replace('pg1374','pg1380').replace('PG1374','PG1380')
        if name=='pg1380_bootstrap_role_refs.py':
            old='str(backend)+"and datname='
            if raw.count(old)!=1:raise ValueError('one actual numeric SQL insertion required')
            raw=raw.replace(old,'str(backend)+" and datname=')
        result[name]=raw
    return result
