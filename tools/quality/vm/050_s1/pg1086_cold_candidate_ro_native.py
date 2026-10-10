"""New-only tools stage or candidate RO action; no placement/current/epoch update."""
import ast
from pg1064_cold_preparation_native_v2 import source as previous


def source():
    raw=previous()
    for old,new in [('pg1063-cold-preparation-frozen-v2.safe.json','pg1085-cold-candidate-ro-frozen-v1.safe.json'),
                    ('pg1062-cold-tools-v1','pg1084-cold-tools-v1'),
                    ('Pg1062ColdOwnedPreparation','Pg1084ColdCandidateRo'),
                    ('pg1064-','pg1086-'),('PG1064_','PG1086_'),
                    ("('stage','prepare')","('stage','prepare-ro')"),
                    ("action=='prepare'and code==0","action=='prepare-ro'and code==0"),
                    ("'finiteColdPreparation':True","'finiteCandidateRoVerification':True"),
                    ("'fullColdPreparationAccepted'","'fullCandidateRoVerified'")]:
        if old not in raw:raise ValueError('fixed ro transport refused')
        raw=raw.replace(old,new)
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1086 new-only candidate RO verification>','exec'),{'__file__':__file__,'__name__':'__main__'})
