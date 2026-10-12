"""SSC277 current Bootstrap layout31/90, frozen1724 failure is not retried."""
import inspect
import pg1724_bootstrap_retained_once_handoff as prior

SLOT='pg1726-bootstrap-current-fd-handoff-v1'

def payload():
    raw=prior.payload().replace(prior.SLOT,SLOT)
    # Exact current independently measured layout, never FD-count inference.
    raw=raw.replace("['29', '32']", "['31', '90']").replace("{'29', '32'}", "{'31', '90'}")
    raw=raw.replace("['29']", "['31']").replace("['32']", "['90']")
    compile(raw,'<SSC277 current31-90 one handoff>','exec');return raw

def main():
    raw=inspect.getsource(prior.main)
    raw=raw.replace("'SSC276'not in text and 'SSC-276'not in text", "'SSC277'not in text and 'SSC-277'not in text")
    raw=raw.replace("with queued_gate(P/'current-management-critical.lock')as acquired:","completed=False\n    with queued_gate(P/'current-management-critical.lock',require_completion=lambda:completed)as acquired:")
    raw=raw.replace("if r.returncode==0 and not acquired.wait(30):", "completed=r.returncode==0\n        if completed and not acquired.wait(30):")
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<new-only current31-90 transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
