"""New-only qualified Java type/build output; previous1092 failed build retained."""
import ast
from pg1092_cold_activation_compile import source as previous


def source():
    raw=previous()
    for old,new in [('from pg1091_cold_activation_sources import files','from pg1094_cold_activation_sources_v2 import files'),
                    ('pg1091-cold-tools-v1','pg1094-cold-tools-v1'),
                    ('Pg1091ColdActivation','Pg1094ColdActivation'),
                    ('PG1092-cold-activation-compile-v1','PG1095-cold-activation-compile-v2'),
                    ('pg1092-cold-activation-frozen-v1.safe.json','pg1095-cold-activation-frozen-v2.safe.json')]:
        if old not in raw:raise ValueError('fixed v2 activation compiler refused')
        raw=raw.replace(old,new)
    marker="commands=[('finite-oracle',"
    if raw.count(marker)!=1:raise ValueError('fixed independent observer phase refused')
    raw=raw.replace(marker,"commands=[('generated-observer-oracle',['python3','-B',str(HERE/'pg1094_cold_activation_observer_test.py'),'-v']),('finite-oracle',")
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1095 new-only activation compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
