"""New-only local-action fixed compiler/transport; old1071place stays unissued."""
import ast
from pathlib import Path


def source():
    raw=Path(__file__).with_name('pg1071_cold_candidate_native.py').read_text()
    for old,new in [('pg1070-cold-candidate-frozen-v1.safe.json','pg1075-cold-candidate-frozen-v2.safe.json'),
                    ('pg1069-cold-tools-v1','pg1074-cold-tools-v1'),
                    ('Pg1069ColdCandidateStage','Pg1074ColdCandidateStage'),
                    ('pg1071-','pg1076-'),('PG1071','PG1076')]:
        if old not in raw:raise ValueError('fixed corrected candidate transport refused')
        raw=raw.replace(old,new)
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1076 fixed new-only transport>','exec'),{'__file__':__file__,'__name__':'__main__'})
