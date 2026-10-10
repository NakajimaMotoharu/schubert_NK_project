"""New-only compiler/input slots, never overwrite the BUG1023 frozen v1."""
import ast
from pathlib import Path


def source():
    raw=Path(__file__).with_name('pg1070_cold_candidate_compile.py').read_text()
    for old,new in [('from pg1069_cold_candidate_sources import files,DIGEST,SOURCE',
                     'from pg1074_cold_candidate_sources_v2 import files\nfrom pg1069_cold_candidate_sources import DIGEST,SOURCE'),
                    ('pg1069-cold-tools-v1','pg1074-cold-tools-v1'),
                    ('Pg1069ColdCandidateStage','Pg1074ColdCandidateStage'),
                    ('pg1071-release-v1.tar','pg1076-release-v1.tar'),
                    ('PG1070-cold-candidate-compile-v1','PG1075-cold-candidate-compile-v2'),
                    ('pg1070-cold-candidate-frozen-v1.safe.json','pg1075-cold-candidate-frozen-v2.safe.json')]:
        if old not in raw:raise ValueError('fixed corrected candidate compiler refused')
        raw=raw.replace(old,new)
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1075 fixed new-only compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
