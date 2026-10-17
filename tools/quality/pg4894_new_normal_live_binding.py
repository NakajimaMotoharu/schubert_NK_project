"""Fresh04bb live ordinary identity; no new start or old source/run inheritance."""
import inspect
import pg4738_new_normal_live_binding as previous
import pg4892_new_normal_root_once as entry
from pg4434_current_candidate_admission_read import authenticate_host

SLOT='pg4894-new-normal-live-binding-v1'
SOURCE,BOM,ONCE=entry.SOURCE,entry.BOM,entry.SLOT


def body():
    raw=entry.observer.bind(previous.body()).replace(previous.ONCE,ONCE)
    return raw+"\nrequire(fields[1]!='fff841d9-2554-4680-b17d-9548bfa79cbb'and fields[3]!='7ab6c953-b2fc-47ae-be96-26a3196ca76d')\nrequire(unit['InvocationID']!='b414b0e1e5ac47e8b5fb8c5ae3d94348')\n"


def main():
    authenticate_host()
    ns={**vars(previous.previous),'SLOT':SLOT,'SOURCE':SOURCE,'BOM':BOM,'ONCE':ONCE,'body':body}
    exec(compile(inspect.getsource(previous.previous.main),'<fresh04bb same-current binding>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
