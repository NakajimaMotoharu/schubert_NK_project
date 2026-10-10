"""BUG1023 corrected local action, new-only cold candidate operator generation."""
import ast
from pg1069_cold_candidate_sources import files as previous


def files():
    result={}
    for name,text in previous().items():
        for old,new in [('Pg1069ColdCandidateStage','Pg1074ColdCandidateStage'),
                        ('pg1069_cold_refs.py','pg1074_cold_refs.py'),
                        ('pg1069-cold-tools-v1','pg1074-cold-tools-v1'),
                        ('pg1069-cold-candidate-v1','pg1074-cold-candidate-v1'),
                        ('pg1071-candidate-input-v1','pg1076-candidate-input-v1'),
                        ('pg1071-release-v1.tar','pg1076-release-v1.tar'),
                        ('PG1069_','PG1074_')]:
            name=name.replace(old,new);text=text.replace(old,new)
        if name.endswith('.py'):ast.parse(text)
        result[name]=text
    return result
