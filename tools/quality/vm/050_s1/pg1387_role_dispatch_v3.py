"""One new immutable corrected role tool stage/prepare, no old generation replay."""
import inspect
import pg1377_bootstrap_role_dispatch as previous

def text():
    raw=inspect.getsource(previous)
    raw=raw.replace('PG1376-bootstrap-role-preflight-v1','PG1386-role-fresh-preflight-v1').replace('pg1376-bootstrap-role-preflight-v1','pg1386-role-fresh-preflight-v1')
    raw=raw.replace('1374','1380').replace('1375','1385').replace('1377','1387')
    raw=raw.replace('pg1368-bootstrap-fixed-ref-handoff-v1','pg1382-role-fixed-ref-handoff-v1')
    compile(raw,'<corrected one-role immutable dispatch>','exec');return raw

def environment():
    env={'__name__':'qualified_role_dispatch'}
    exec(compile(text(),'<corrected role dispatch module>','exec'),env)
    return env

if __name__=='__main__':raise SystemExit(environment()['main']())
