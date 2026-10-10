"""New generated family/slot after initial unimplemented compile, no old output overwrite."""
import ast
from pg1091_cold_activation_sources import files as previous


def files():
    result={}
    for name,text in previous().items():
        for old,new in [('Pg1091ColdActivation','Pg1094ColdActivation'),
                        ('pg1091_cold_refs.py','pg1094_cold_refs.py'),
                        ('pg1091-cold-tools-v1','pg1094-cold-tools-v1'),
                        ('pg1091-cold-activate-v1','pg1094-cold-activate-v1'),
                        ('pg1091-approval.part','pg1094-approval.part'),
                        ('PG1091_','PG1094_')]:
            name=name.replace(old,new);text=text.replace(old,new)
        if name.endswith('.py'):ast.parse(text)
        result[name]=text
    return result
