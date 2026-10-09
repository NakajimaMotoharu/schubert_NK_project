"""New current40ef A01 against untouched Current baseline; old A01 never reused."""
import ast
from pathlib import Path
from pg876_a01_current import code as previous
R=Path(__file__).resolve().parent
def code():
    raw=previous()
    for a,b in (('PG876','PG961'),('pg876','pg961'),('pg871','pg956'),('pg872-ordinary-once-v1','pg957-ordinary-once-v1'),('pg870-ordinary-before-v1','pg954-ordinary-before-v1'),('e01612fcd7f2752df5ae0836b78538fd5e87f120','40ef6e894573d2ffab1d1732124960f9c98d5f97'),('20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524'),('0.1.0-PG862','0.1.0-PG932')):
        assert a in raw,a;raw=raw.replace(a,b)
    ast.parse(raw);return raw
if __name__=='__main__':
    exec(compile(code(),'<961 actual current40ef A01>','exec'),{'__file__':str(R/'pg961_current_a01.py'),'__name__':'__main__'})
