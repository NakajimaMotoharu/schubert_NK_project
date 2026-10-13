"""Independent read-only current PG2126 parent/run identity from once-issued Job."""
import inspect
import pg2074_current_newrun_live_binding as prior
from pg2176_newsource_normal_observer import SOURCE,BOM

SLOT='pg2180-newsource-live-binding-v1'


def body():
    raw=prior.body().replace('PG1846','PG2126')
    marker="require(fields[1]!='4148e3e8-f107-431a-ab27-d6e6d1f1772e'and fields[3]!='e31b627c-c0e2-4120-bd64-c0777479e800')"
    if raw.count(marker)!=1:raise ValueError('one prior run rejection boundary required')
    return raw.replace(marker,marker+"\nrequire(fields[1]!='a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75'and fields[3]!='9026b2ab-bb42-49cd-a2bd-4c661049dce3')")


def entry():
    raw=inspect.getsource(prior.transport.main).replace('pg2015-completed-run-fresh-resume-once-v1','pg2178-newsource-noargs-once-v1')
    ns={**prior.transport.__dict__,'SOURCE':SOURCE,'BOM':BOM,'SLOT':SLOT,'body':body}
    exec(compile(raw,'<current newsource read-only binding entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
