"""New tool stage or one fixed oldpart preservation, never activation replay."""
import ast
from pg1096_cold_activation_native_v2 import source as previous


def source():
    raw=previous()
    for old,new in [('pg1095-cold-activation-frozen-v2.safe.json','pg1101-linked-preservation-frozen-v1.safe.json'),
        ('pg1094-cold-tools-v1','pg1100-linked-tools-v1'),('Pg1094ColdActivation','Pg1100LinkedPreservation'),
        ('pg1096-','pg1102-'),('PG1096_','PG1102_'),("('stage','activate')","('stage','preserve')"),
        ("action=='activate'and code==0","action=='preserve'and code==0"),
        ('finiteColdActivation','linkedOriginalPreservation')]:
        if old not in raw:raise ValueError('fixed linked transport refused')
        raw=raw.replace(old,new)
    raw=raw.replace("'/opt/schubert-nk/releases/0.1.0-PG932')\narchive=", "'/opt/schubert-nk/releases/0.1.0-PG1068')\narchive=")
    # Tool ABI remains qualified PG932; current pointer already names PG1068.
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1102 new linked preservation>','exec'),{'__file__':__file__,'__name__':'__main__'})
