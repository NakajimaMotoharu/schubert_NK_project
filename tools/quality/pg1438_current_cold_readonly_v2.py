"""New-only full-vector cold proof; old1437 failure is retained, no boot replay."""
import ast
import inspect
import pg1437_current_cold_readonly as previous
import cold_unit_file_vector as vector

ORIGINAL_PAYLOAD=previous.payload


def payload():
    raw=ORIGINAL_PAYLOAD()
    marker="  require(hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()==expected)"
    assert raw.count(marker)==1
    replacement="  p=pathlib.Path(path);observed=metadata(p);require(UNIT_VECTOR['matches'](expected,observed,hashlib.sha256(p.read_bytes()).hexdigest()) and metadata(p)==observed)"
    raw=raw.replace(marker,replacement).replace('pg1437-current-cold-readonly-v1','pg1438-current-cold-readonly-v2')
    raw="UNIT_VECTOR={};exec("+repr(inspect.getsource(vector))+",UNIT_VECTOR)\n"+raw
    ast.parse(raw);return raw


if __name__=='__main__':
    namespace=dict(previous.__dict__,OUT=previous.OUT.with_name('pg1438-cold-ro-v2'),payload=payload)
    main_source=inspect.getsource(previous.main).replace('PG1437-current-cold-readonly-v1','PG1438-current-cold-readonly-v2')
    exec(compile(main_source,'<new full-vector cold read-only transport>','exec'),namespace)
    raise SystemExit(namespace['main']())
