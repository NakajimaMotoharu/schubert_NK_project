"""Bind captured current Root generation to a new activation, keeping original cutoff."""
import inspect
from pyflakes.api import check
import pg2019_fresh_resume_live_binding_complete as previous
from pg2360_current_completed_resume_once import SOURCE,BOM,RUN

SLOT='pg2362-current-resume-live-binding-v1'


def body():
    raw=previous.body()
    for a,b in [('3d69f5af-6bac-46b1-a540-7591c4a79a0d','b2d6f605-61cf-425f-8fbd-12d606f6ee66'),('3d69f5af6bac46b1a5407591c4a79a0d','b2d6f60561cf425f8fbd12d606f6ee66'),('PG1846','PG2126'),('4148e3e8-f107-431a-ab27-d6e6d1f1772e',RUN),('2026-10-12T18:20:32.598894Z','2026-10-13T15:01:53.237266Z'),('9adbf05a-61d0-408b-b51d-ab19c7e5b16a','9be93262-fbb2-438f-b2b0-c4a27f5563a4')]:raw=raw.replace(a,b)
    if check('SOURCE="test"\nDIGEST="test"\nEXPECTED={}\n'+raw,'<current new activation binding>'):raise ValueError('all new binding globals required')
    return raw


def main():
    raw=inspect.getsource(previous.prior.main).replace('pg2015-completed-run-fresh-resume-once-v1','pg2360-current-completed-resume-once-v1')
    ns={**previous.prior.__dict__,'SOURCE':SOURCE,'BOM':BOM,'RUN':RUN,'SLOT':SLOT,'body':body}
    exec(compile(raw,'<current new activation binding transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
