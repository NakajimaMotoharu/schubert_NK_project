"""New-only fixed v2 activation family; previous1093 never issued."""
import ast
from pg1093_cold_activation_native import source as previous


def source():
    raw=previous()
    for old,new in [('pg1092-cold-activation-frozen-v1.safe.json','pg1095-cold-activation-frozen-v2.safe.json'),
                    ('pg1091-cold-tools-v1','pg1094-cold-tools-v1'),
                    ('Pg1091ColdActivation','Pg1094ColdActivation'),
                    ('pg1093-','pg1096-'),('PG1093_','PG1096_')]:
        if old not in raw:raise ValueError('fixed v2 activation transport refused')
        raw=raw.replace(old,new)
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1096 new-only cold activation transport>','exec'),{'__file__':__file__,'__name__':'__main__'})
