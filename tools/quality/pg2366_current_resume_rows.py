"""Independent all-column current completed-run resume oracle from sealed before."""
import inspect
from pyflakes.api import check
import pg2023_fresh_resume_rows_oracle as previous
from pg2360_current_completed_resume_once import SOURCE,RUN,BEFORE

SLOT='pg2366-current-resume-rows-v1'


def oracle_source():
    raw=previous.oracle_source()
    old="progress[0]['protected_count']==4"
    if raw.count(old)!=1:raise ValueError('one fixed completed progress fixture boundary required')
    return raw.replace(old,"progress[0]['protected_count']==10")


def qualify(*args):
    ns={};exec(compile(oracle_source(),'<independent current rows oracle>','exec'),ns);return ns['qualify'](*args)


def payload():
    raw=previous.payload()
    old=previous.oracle_source()
    if raw.count(old)!=1:raise ValueError('one all-column independent oracle required')
    raw=raw.replace(old,oracle_source())
    for a,b in [(previous.SLOT,SLOT),('pg2015-completed-run-fresh-resume-once-v1','pg2360-current-completed-resume-once-v1'),('3d69f5af-6bac-46b1-a540-7591c4a79a0d','b2d6f605-61cf-425f-8fbd-12d606f6ee66'),('fd6412f31de9af59219a0fe28f49ce0d073b074a7ff83ca3516a22e462568b83',BEFORE),('4148e3e8-f107-431a-ab27-d6e6d1f1772e',RUN),('e31b627c-c0e2-4120-bd64-c0777479e800','e1429ac8-f3dd-4e8c-83d2-1926c4ba8440'),('2026-10-12T18:20:32.598894Z','2026-10-13T15:01:53.237266Z'),('2026-10-13T01:15:32.188849+00:00','2026-10-13T18:52:04.958394+00:00')]:raw=raw.replace(a,b)
    if check(raw,'<current resume rows full source>'):raise ValueError('all current oracle globals required')
    compile(raw,'<current completed resume rows>','exec');return raw


def main():
    raw=inspect.getsource(previous.main).replace('pg2021-fresh-resume-terminal-receipt-v1','pg2364-current-resume-terminal-v1')
    ns={**previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<current rows independent transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
