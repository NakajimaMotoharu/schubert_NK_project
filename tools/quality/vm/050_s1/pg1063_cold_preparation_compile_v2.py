"""Reuse qualified compiler algorithm, new v2 source/output identity only."""
import ast
from pathlib import Path
from pg1062_cold_preparation_sources_v2 import files


def source():
    raw=Path(__file__).with_name('pg1038_cold_preparation_compile.py').read_text()
    raw=raw.replace('from pg1037_cold_preparation_sources import files','from pg1062_cold_preparation_sources_v2 import files')
    for old,new in [('pg1037-cold-tools-v1','pg1062-cold-tools-v1'),
                    ('Pg1037ColdOwnedPreparation','Pg1062ColdOwnedPreparation'),
                    ('pg1037_cold_preparation_sources_test.py','pg1062_cold_preparation_sources_v2_test.py'),
                    ('pg1038-cold-preparation-frozen-v1.safe.json','pg1063-cold-preparation-frozen-v2.safe.json'),
                    ('PG1038-cold-preparation-compile-v1','PG1063-cold-preparation-compile-v2')]:
        if old not in raw:raise ValueError('fixed v2 compiler profile refused')
        raw=raw.replace(old,new)
    ast.parse(raw);return raw


if __name__=='__main__':
    exec(compile(source(),'<PG1063 frozen new compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
