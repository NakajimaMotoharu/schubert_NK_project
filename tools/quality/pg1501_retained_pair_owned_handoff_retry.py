"""New-only after SQL proof refusal, which issued no TERM; old slots preserved."""
import inspect
import pg1499_retained_pair_owned_handoff as previous

def payload():return previous.payload().replace('pg1499-retained-publication-pair-handoff-v1','pg1501-retained-publication-pair-handoff-v3')
def main():
    raw=inspect.getsource(previous.main).replace('pg1499-retained-publication-pair-handoff-v1','pg1501-retained-publication-pair-handoff-v3')
    ns={**previous.__dict__,'payload':payload};exec(compile(raw,'<new-only same-peer handoff>','exec'),ns);return ns['main']()
if __name__=='__main__':raise SystemExit(main())
