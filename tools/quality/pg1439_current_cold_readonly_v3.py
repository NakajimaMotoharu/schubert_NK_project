"""New-only current full24 SQL cap; preserves both previous cold failures."""
import ast
import inspect
import pg1438_current_cold_readonly_v2 as previous
import cold_capture_bound as bound


def payload():
    raw=previous.payload()
    marker="for line in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).splitlines():"
    assert raw.count(marker)==1
    raw=raw.replace(marker,marker.replace('sql]).','sql],67108864).'))
    old='require(r.returncode == 0 and len(r.stdout) <= limit)'
    assert raw.count(old)==1
    raw=raw.replace(old,"require(CAPTURE_BOUND['accepted'](r.returncode,len(r.stdout),limit))")
    raw=raw.replace('pg1438-current-cold-readonly-v2','pg1439-current-cold-readonly-v3')
    raw='CAPTURE_BOUND={};exec('+repr(inspect.getsource(bound))+',CAPTURE_BOUND)\n'+raw
    ast.parse(raw);return raw


if __name__=='__main__':
    original=previous.previous
    namespace=dict(original.__dict__,OUT=original.OUT.with_name('pg1439-cold-ro-v3'),payload=payload)
    source=inspect.getsource(original.main).replace('PG1437-current-cold-readonly-v1','PG1439-current-cold-readonly-v3')
    exec(compile(source,'<new current full24 bounded readonly transport>','exec'),namespace)
    raise SystemExit(namespace['main']())
