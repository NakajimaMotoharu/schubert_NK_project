"""Read-only same-generation296 Root/peer proof; no oldowner/permit inheritance."""
import inspect
import pg5024_new_normal_live_binding as previous
import pg5470_new_normal_root_once as entry
from pg4996_resume_connection import authenticate_host

SLOT='pg5472-new-normal-live-binding-v1'
SOURCE,BOM,ONCE=entry.SOURCE,entry.BOM,entry.SLOT


def body():return entry.observer.bind(previous.body()).replace(previous.ONCE,ONCE)


def main():
    authenticate_host();template=previous.previous.previous.previous
    ns={**vars(template),'SLOT':SLOT,'SOURCE':SOURCE,'BOM':BOM,'ONCE':ONCE,'body':body}
    exec(compile(inspect.getsource(template.main),'<fresh296 same-current binding>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
