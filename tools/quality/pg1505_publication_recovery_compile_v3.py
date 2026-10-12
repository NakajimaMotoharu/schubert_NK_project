"""Fresh frozen owner/refs after broker mmap correction; old tools are untouched."""
import inspect
import pg1490_publication_recovery_compile as previous
from pg1505_publication_recovery_sources_v3 import java,refs

def main():
    raw=inspect.getsource(previous.main)
    for old,new in [('Pg1489PublicationOnlyRecovery','Pg1505PublicationOnlyRecovery'),('pg1489_publication_recovery_refs.py','pg1505_publication_recovery_refs.py'),('pg1489-publication-only-tools-v1','pg1505-publication-only-tools-v3'),('pg1489_publication_recovery_sources_test.py','pg1505_publication_recovery_sources_v3_test.py'),('PG1490-publication-recovery-compile-v1','PG1505-publication-recovery-compile-v3'),('pg1490-publication-recovery-frozen-v1.safe.json','pg1505-publication-recovery-frozen-v3.safe.json')]:
        if old not in raw:raise ValueError('corrected owned operator compiler binding refused')
        raw=raw.replace(old,new)
    ns={**previous.__dict__,'java':java,'refs':refs};exec(compile(raw,'<new current typed mapping compiler>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
