"""SSC277 separate current whole post for actual1726, no actor operations."""
import inspect
import pg1725_bootstrap_recovery_independent_post as prior

SLOT='pg1727-bootstrap-recovery-full-post-v1'

def payload():
    # Rebind the actual manifest producer and guest reservation namespace only.
    ns=dict(prior.payload.__globals__)
    ns['BODY']=prior.BODY.replace('pg1724-bootstrap-retained-handoff-v1','pg1726-bootstrap-current-fd-handoff-v1')
    ns['SLOT']=SLOT
    code=inspect.getsource(prior.payload).replace('pg1724-bootstrap-retained-handoff-v1','pg1726-bootstrap-current-fd-handoff-v1')
    exec(compile(code,'<actual1726 post source>','exec'),ns);return ns['payload']()

def main():
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(prior.main),'<new-only1726 post transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
