"""New-only one noargs root after original Ref-lifetime refusal (old start0)."""
import inspect
import pg1598_current_ordinary_once as prior
from pg1599_current_ordinary_once_sources_v2 import payload

def main():
    raw=inspect.getsource(prior.main).replace('pg1598-current-ordinary-once-v1','pg1600-current-ordinary-once-v2')
    ns={**prior.__dict__,'payload':payload};exec(compile(raw,'<fresh fixed once noargs source>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
