"""Read only new ordinary Root identity; old failed and old normal cohorts forbidden."""
import inspect
import pg4246_fresh_current_live_binding as previous
import pg4576_current_fresh_noargs_once as entry
from pg2814_network_newboot_readonly import one
from pg4434_current_candidate_admission_read import authenticate_host

SLOT='pg4578-current-live-binding-v1'
SOURCE,BOM,ONCE=entry.SOURCE,entry.BOM,entry.SLOT


def body():
    raw=entry.observer.bind(previous.body())
    return raw+"\nrequire(fields[1]!='b1ba37cb-9b2b-469b-a5f2-b0e6d8c97cd1'and fields[3]!='8314450e-0dd5-4986-875c-81f73e1b50b2')\nrequire(unit['InvocationID']!='bbcdb69957764d489a9c757b441542fd')\n"


def main():
    authenticate_host()
    raw=inspect.getsource(previous.main)
    ns={**vars(previous),'SLOT':SLOT,'SOURCE':SOURCE,'BOM':BOM,'ONCE':ONCE,'body':body}
    raw=one(raw,'original new entry actual0 first','original964e entry actual0 first')
    exec(compile(raw,'<distinct964e Root binding read dispatcher>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
