"""Fresh output after pre-signal input-guard rejection; no old handoff slot reuse."""
import inspect
import pg1499_retained_pair_owned_handoff as previous

def payload():return previous.payload().replace('pg1499-retained-publication-pair-handoff-v1','pg1500-retained-publication-pair-handoff-v2')

def main():
    entry=inspect.getsource(previous.main).replace('pg1499-retained-publication-pair-handoff-v1','pg1500-retained-publication-pair-handoff-v2')
    ns={**previous.__dict__,'payload':payload}
    exec(compile(entry,'<new-only exact pair once handoff>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
