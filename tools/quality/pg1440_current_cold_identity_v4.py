"""Fresh all-scope current cold capture with strict same run identity."""
import ast
import inspect
import pg1439_current_cold_readonly_v3 as previous

RUN='PG1440-current-cold-readonly-v4'
SLOT='pg1440-current-cold-readonly-v4'


def payload():
    raw=previous.payload().replace('pg1439-current-cold-readonly-v3',SLOT)
    old='PG1437-current-cold-readonly-v1'
    assert raw.count(old)==1
    raw=raw.replace(old,RUN)
    syntax=ast.parse(raw)
    values=[n.value for n in ast.walk(syntax) if isinstance(n,ast.Constant) and type(n.value)is str]
    assert RUN in values and all(not v.startswith(('PG1437-current','PG1438-current','PG1439-current')) for v in values)
    assert SLOT in raw
    return raw


if __name__=='__main__':
    original=previous.previous.previous
    namespace=dict(original.__dict__,OUT=original.OUT.with_name('pg1440-cold-ro-v4'),payload=payload)
    source=inspect.getsource(original.main).replace('PG1437-current-cold-readonly-v1',RUN)
    marker="value=json.loads((OUT/'observer.private.log').read_bytes());record['safeGuestResult']=value"
    assert source.count(marker)==1
    source=source.replace(marker,"value=json.loads((OUT/'observer.private.log').read_bytes());assert value['run']==record['run'];record['safeGuestResult']=value")
    exec(compile(source,'<same-run identity current cold readonly transport>','exec'),namespace)
    raise SystemExit(namespace['main']())
