"""New-only current-end full capture; old773 failed remains immutable."""
from pathlib import Path
from pg662_sources import replace
from pg773_failure_full import source as prior

R=Path(__file__).resolve().parent


def source():
    pure=(R/'pg774_live_rows.py').read_text().replace('import json\n','')
    return replace(prior().replace('pg773-failure-full758-v1','pg774-failure-full758-v1'),
        (("allrows=rows();assert allrows==expected_rows and rows()==allrows",pure+"\nallrows=rows();assert preserved(expected_rows,allrows)and rows()==allrows"),))


if __name__=='__main__':
    exec(compile(source(),'<new774 currentend fixed full24>','exec'),{'__file__':str(R/'pg774_failure_full.py'),'__name__':'__main__'})
