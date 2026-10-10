"""Fixed Source compile for SSC249 candidate RO; no candidate rebuild or bundle."""
import ast
from pathlib import Path


def source():
    raw=Path(__file__).with_name('pg1038_cold_preparation_compile.py').read_text()
    for old,new in [('from pg1037_cold_preparation_sources import files','from pg1084_cold_candidate_ro_sources import files'),
                    ('pg1037-cold-tools-v1','pg1084-cold-tools-v1'),
                    ('Pg1037ColdOwnedPreparation','Pg1084ColdCandidateRo'),
                    ('pg1037_cold_preparation_sources_test.py','pg1084_cold_candidate_ro_sources_test.py'),
                    ('PG1038-cold-preparation-compile-v1','PG1085-cold-candidate-ro-compile-v1'),
                    ('pg1038-cold-preparation-frozen-v1.safe.json','pg1085-cold-candidate-ro-frozen-v1.safe.json')]:
        if old not in raw:raise ValueError('fixed ro compiler refused')
        raw=raw.replace(old,new)
    marker="commands=[('python-oracle',"
    if raw.count(marker)!=1:raise ValueError('fixed compiler oracle refused')
    raw=raw.replace(marker,"commands=[('finite-oracle',['python3','-B',str(HERE/'pg1083_cold_publication_contract_test.py'),'-v']),('python-oracle',")
    ast.parse(raw);return raw


if __name__=='__main__':exec(compile(source(),'<PG1085 fixed candidate ro compiler>','exec'),{'__file__':__file__,'__name__':'__main__'})
