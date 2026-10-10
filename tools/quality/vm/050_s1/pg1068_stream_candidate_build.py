"""New-only signed d5/1018 candidate, current40ef/PG932 and original baseline untouched."""
import ast
from pathlib import Path
from pg932_candidate_build import source as previous


def source():
    raw=previous()
    for old,new in (
        ('pg931_candidate_contract','pg1067_stream_candidate_contract'),
        ("SOURCE = '40ef6e894573d2ffab1d1732124960f9c98d5f97'","SOURCE = 'd5b00104280028d9ea81b44c1d1c805f3c2861ed'"),
        ("OLD_SOURCE = 'e01612fcd7f2752df5ae0836b78538fd5e87f120'","OLD_SOURCE = '40ef6e894573d2ffab1d1732124960f9c98d5f97'"),
        ('PG932','NEXT_PG1068'),('pg932','NEXT_pg1068'),('PG862','PG932'),('pg862','pg932'),
        ('NEXT_PG1068','PG1068'),('NEXT_pg1068','pg1068'),
        ('pg926-body-six-host-v1','pg1018-stream-six-host-v2'),
        ('4ae512d3b3a8e85d81fcd8e9ef04279fff58114c42e9b158adc61299d8211fdf','c94cf95cddaef9fae4d3db02d3a732ee17a5ffdcc700714b14b4694fb077aab1'),
        ('20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524'),
        ('tests\'] == 3560','tests\'] == 3563'),("'changedClasses': 4","'changedClasses': 1"),
    ):
        if old not in raw:raise ValueError('fixed d5 candidate profile refused')
        raw=raw.replace(old,new)
    ast.parse(raw);return raw


if __name__=='__main__':
    exec(compile(source(),'<PG1068 signed qualified stream candidate>','exec'),{'__file__':__file__,'__name__':'__main__'})
