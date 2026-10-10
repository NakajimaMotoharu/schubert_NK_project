"""New-only fixed family compiler; old1070/1075 frozen remain unmodified."""
import ast
from pg1075_cold_candidate_compile_v2 import source as previous


def source():
    raw=previous()
    for old,new in [('from pg1074_cold_candidate_sources_v2 import files','from pg1079_cold_candidate_sources_v3 import files'),
                    ('pg1074-cold-tools-v1','pg1079-cold-tools-v1'),
                    ('Pg1074ColdCandidateStage','Pg1079ColdCandidateStage'),
                    ('pg1076-release-v1.tar','pg1081-release-v1.tar'),
                    ('PG1075-cold-candidate-compile-v2','PG1080-cold-candidate-compile-v3'),
                    ('pg1075-cold-candidate-frozen-v2.safe.json','pg1080-cold-candidate-frozen-v3.safe.json')]:
        if old not in raw:raise ValueError('fixed v3 compiler refused')
        raw=raw.replace(old,new)
    marker="commands=[('python-oracle',"
    if raw.count(marker)!=1:raise ValueError('fixed compiler oracle phases refused')
    raw=raw.replace(marker,"commands=[('family-oracle',['python3','-B',str(HERE/'pg1079_cold_candidate_family_test.py'),'-v']),('python-oracle',")
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1080 new-only fixed family compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
