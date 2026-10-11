"""Fresh immutable actor/tool/save after BUG1114 import dependency correction; no old slot reuse."""
import inspect
import pg1442_current_cold_compile as compiler
import pg1490_publication_recovery_compile as previous
from pg1489_publication_recovery_sources import java as old_java,refs as old_refs

def remap(raw):
    return raw.replace('Pg1489PublicationOnlyRecovery','Pg1493PublicationOnlyRecovery').replace('pg1489-publication-only-tools-v1','pg1493-publication-only-tools-v2').replace('pg1489_publication_recovery_refs.py','pg1493_publication_recovery_refs.py').replace('pg1492-publication-only-recovery-v1','pg1495-publication-only-recovery-v2').replace('PG1492_','PG1495_')

def main():
    raw=inspect.getsource(previous.main)
    for old,new in [('Pg1489PublicationOnlyRecovery','Pg1493PublicationOnlyRecovery'),('pg1489_publication_recovery_refs.py','pg1493_publication_recovery_refs.py'),('pg1489-publication-only-tools-v1','pg1493-publication-only-tools-v2'),('PG1490-publication-recovery-compile-v1','PG1493-publication-recovery-compile-v2'),('pg1490-publication-recovery-frozen-v1.safe.json','pg1493-publication-recovery-frozen-v2.safe.json')]:
        if old not in raw:raise ValueError('immutable corrected actor source binding refused')
        raw=raw.replace(old,new)
    ns={**previous.__dict__,'compiler':compiler,'java':lambda:remap(old_java()),'refs':lambda:remap(old_refs())}
    exec(compile(raw,'<corrected new-only current owner compiler>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
