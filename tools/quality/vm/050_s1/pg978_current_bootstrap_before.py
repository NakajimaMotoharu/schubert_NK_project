"""Fresh full current968 enriched Bootstrap before; no unit start or credential creation."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
def source():
    raw=(R/'pg895_bootstrap_before.py').read_text()
    for a,b in (('pg890_terminal_final','pg968_current_terminal_final'),('pg890','pg968'),('PG890','PG968'),('pg895','pg978'),('PG895','PG978'),('pg885','pg960'),('pg887','pg963'),('e01612fcd7f2752df5ae0836b78538fd5e87f120','40ef6e894573d2ffab1d1732124960f9c98d5f97'),('20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524'),('==584','==604')):
        assert a in raw,a;raw=raw.replace(a,b)
    ast.parse(raw);return raw
if __name__=='__main__':
    exec(compile(source(),'<978 independent current Bootstrap before>','exec'),{'__file__':str(R/'pg978_current_bootstrap_before.py'),'__name__':'__main__'})
