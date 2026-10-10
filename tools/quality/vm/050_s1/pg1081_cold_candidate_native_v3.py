"""New-only exact family transport; failed1076 is never restarted or re-staged."""
import ast
from pg1076_cold_candidate_native_v2 import source as previous


def source():
    raw=previous()
    for old,new in [('pg1075-cold-candidate-frozen-v2.safe.json','pg1080-cold-candidate-frozen-v3.safe.json'),
                    ('pg1074-cold-tools-v1','pg1079-cold-tools-v1'),
                    ('Pg1074ColdCandidateStage','Pg1079ColdCandidateStage'),
                    ('pg1076-','pg1081-'),('PG1076','PG1081')]:
        if old not in raw:raise ValueError('fixed v3 native transport refused')
        raw=raw.replace(old,new)
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1081 new-only fixed family transport>','exec'),{'__file__':__file__,'__name__':'__main__'})
