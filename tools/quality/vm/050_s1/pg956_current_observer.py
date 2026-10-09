"""Fresh40ef/932 observer, never automatic start/stop or prior observer reuse."""
import ast
from pathlib import Path
from pg871_ordinary_observer import source as previous
R=Path(__file__).resolve().parent
def source():
    raw=previous()
    for a,b in (('pg871','pg956'),('PG871','PG956'),('PG862','PG932'),('pg870-ordinary-before-v1','pg954-ordinary-before-v1'),('e01612fcd7f2752df5ae0836b78538fd5e87f120','40ef6e894573d2ffab1d1732124960f9c98d5f97'),('20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524')):
        assert a in raw,a;raw=raw.replace(a,b)
    ast.parse(raw);return raw
if __name__=='__main__':
    exec(compile(source(),'<956 immutable new-source observer>','exec'),{'__file__':str(R/'pg956_current_observer.py'),'__name__':'__main__'})
