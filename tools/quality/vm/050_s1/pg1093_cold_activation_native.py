"""New-only fixed activation tool stage or one real code-only activation."""
import ast
from pg1064_cold_preparation_native_v2 import source as previous


def source():
    raw=previous()
    for old,new in [('pg1063-cold-preparation-frozen-v2.safe.json','pg1092-cold-activation-frozen-v1.safe.json'),
                    ('pg1062-cold-tools-v1','pg1091-cold-tools-v1'),
                    ('Pg1062ColdOwnedPreparation','Pg1091ColdActivation'),
                    ('pg1064-','pg1093-'),('PG1064_','PG1093_'),
                    ("('stage','prepare')","('stage','activate')"),
                    ("action=='prepare'and code==0","action=='activate'and code==0"),
                    ("'finiteColdPreparation':True","'finiteColdActivation':True"),
                    ("'fullColdPreparationAccepted'","'finiteColdActivationAccepted'")]:
        if old not in raw:raise ValueError('fixed activation transport refused')
        raw=raw.replace(old,new)
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1093 new-only fixed cold code-only activation>','exec'),{'__file__':__file__,'__name__':'__main__'})
