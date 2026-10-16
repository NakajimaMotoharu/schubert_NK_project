"""Read-only new ordinary Root identity; no renewal/start and no old cohort reuse."""
import inspect
import pg4246_fresh_current_live_binding as previous
import pg4736_new_normal_root_once as entry
from pg4434_current_candidate_admission_read import authenticate_host

SLOT='pg4738-new-normal-live-binding-v1'
SOURCE,BOM,ONCE=entry.SOURCE,entry.BOM,entry.SLOT


def body():
    raw=entry.observer.bind(previous.body())
    return raw+"\nrequire(fields[1]!='3c71efc3-5bc0-4e31-8477-96e229a60806'and fields[3]!='e0c44d1b-a451-4ad7-b602-b04215d3e0eb')\nrequire(unit['InvocationID']!='9a28ccb26bff42a4900dae95ade7a471')\n"


def main():
    authenticate_host()
    ns={**vars(previous),'SLOT':SLOT,'SOURCE':SOURCE,'BOM':BOM,'ONCE':ONCE,'body':body}
    exec(compile(inspect.getsource(previous.main),'<new normal actual Root binding>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
