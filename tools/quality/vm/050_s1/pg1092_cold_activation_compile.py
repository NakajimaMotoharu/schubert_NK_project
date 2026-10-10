"""Source-fixed compile/independent finite and IO oracles for cold activation."""
import ast
from pathlib import Path


def source():
    raw=Path(__file__).with_name('pg1038_cold_preparation_compile.py').read_text()
    for old,new in [('from pg1037_cold_preparation_sources import files','from pg1091_cold_activation_sources import files'),
                    ('pg1037-cold-tools-v1','pg1091-cold-tools-v1'),
                    ('Pg1037ColdOwnedPreparation','Pg1091ColdActivation'),
                    ('pg1037_cold_preparation_sources_test.py','pg1091_cold_activation_sources_test.py'),
                    ('PG1038-cold-preparation-compile-v1','PG1092-cold-activation-compile-v1'),
                    ('pg1038-cold-preparation-frozen-v1.safe.json','pg1092-cold-activation-frozen-v1.safe.json')]:
        if old not in raw:raise ValueError('fixed activation compiler refused')
        raw=raw.replace(old,new)
    marker="commands=[('python-oracle',"
    if raw.count(marker)!=1:raise ValueError('fixed compiler phases refused')
    raw=raw.replace(marker,"commands=[('finite-oracle',['python3','-B',str(HERE/'pg1083_cold_publication_contract_test.py'),'-v']),('exchange-oracle',['python3','-B',str(HERE/'pg1088_cold_exchange_io_test.py'),'-v']),('capture-oracle',['python3','-B',str(HERE/'pg1090_cold_finite_capture_test.py'),'-v']),('python-oracle',")
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1092 fixed cold activation compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
