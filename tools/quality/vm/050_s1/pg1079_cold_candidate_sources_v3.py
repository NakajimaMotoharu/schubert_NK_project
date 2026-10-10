"""Corrected local candidate action and exact parent/child place, new v3 slots."""
import ast
from pg1074_cold_candidate_sources_v2 import files as previous


def files():
    result={}
    for name,text in previous().items():
        for old,new in [('Pg1074ColdCandidateStage','Pg1079ColdCandidateStage'),
                        ('pg1074_cold_refs.py','pg1079_cold_refs.py'),
                        ('pg1074-cold-tools-v1','pg1079-cold-tools-v1'),
                        ('pg1074-cold-candidate-v1','pg1079-cold-candidate-v1'),
                        ('pg1076-candidate-input-v1','pg1081-candidate-input-v1'),
                        ('pg1076-release-v1.tar','pg1081-release-v1.tar'),
                        ('PG1074_','PG1079_')]:
            name=name.replace(old,new);text=text.replace(old,new)
        if name.endswith('.py'):ast.parse(text)
        result[name]=text
    return result
