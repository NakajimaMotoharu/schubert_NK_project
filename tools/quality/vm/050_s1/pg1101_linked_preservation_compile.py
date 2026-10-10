"""New-only linked preservation Java/Python qualification; no guest action."""
import ast
from pg1095_cold_activation_compile_v2 import source as previous


def source():
    raw=previous()
    for old,new in [('from pg1094_cold_activation_sources_v2 import files','from pg1100_linked_preservation_sources import files'),
        ('pg1094-cold-tools-v1','pg1100-linked-tools-v1'),('Pg1094ColdActivation','Pg1100LinkedPreservation'),
        ('PG1095-cold-activation-compile-v2','PG1101-linked-preservation-compile-v1'),
        ('pg1095-cold-activation-frozen-v2.safe.json','pg1101-linked-preservation-frozen-v1.safe.json')]:
        if old not in raw:raise ValueError('fixed linked compiler profile refused')
        raw=raw.replace(old,new)
    marker="commands=[('generated-observer-oracle',"
    if raw.count(marker)!=1:raise ValueError('linked qualification phase refused')
    raw=raw.replace(marker,"commands=[('linked-source-oracle',['python3','-B',str(HERE/'pg1100_linked_preservation_sources_test.py'),'-v']),('partial-oracle',['python3','-B',str(HERE/'pg1097_partial_exchange_contract_test.py'),'-v']),('generated-observer-oracle',")
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1101 new linked compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
