"""Read-only independent noargs Root binding; start tool already exited, immutable Main unchanged."""
import ast
import inspect
from pg1321_live_root_binding import BODY
import pg2017_fresh_resume_live_binding as transport
from pg2070_current_newrun_observer import SOURCE,BOM

SLOT='pg2074-current-newrun-live-binding-v1'


def body():
    raw=BODY.replace('cbca8738-3b24-4090-b77c-bf029677cdd6','3d69f5af-6bac-46b1-a540-7591c4a79a0d').replace('cbca87383b244090b77cbf029677cdd6','3d69f5af6bac46b1a5407591c4a79a0d').replace('PG1292','PG1846')
    raw=raw.replace('import datetime,hashlib,json,os,pathlib,stat,subprocess,time,uuid','import datetime,hashlib,json,os,pathlib,stat,subprocess,uuid')
    marker="for name,expected in [('runs/'"
    if raw.count(marker)!=1:raise ValueError('one noargs newrun independent identity boundary required')
    raw=raw.replace(marker,"require(fields[1]!='4148e3e8-f107-431a-ab27-d6e6d1f1772e'and fields[3]!='e31b627c-c0e2-4120-bd64-c0777479e800')\n"+marker)
    compile(raw,'<noargs actual newrun binding>','exec');return raw


def entry():
    raw=inspect.getsource(transport.main).replace('pg2015-completed-run-fresh-resume-once-v1','pg2072-current-noargs-newrun-once-v1')
    ast.parse(raw)
    ns={**transport.__dict__,'SOURCE':SOURCE,'BOM':BOM,'SLOT':SLOT,'body':body}
    exec(compile(raw,'<read-only current noargs capture entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
