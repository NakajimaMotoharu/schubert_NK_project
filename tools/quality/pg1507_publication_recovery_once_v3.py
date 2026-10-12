"""Separate new-only recovery after prior management pair fully reclaimed; no failed slot replay."""
import inspect
import pg1495_publication_recovery_once as previous
from pg1506_publication_recovery_stage_v3 import OUTNAME

def valid_receipt(data):
    return type(data)is bytes and data==b'PG1292 STAGE PINNED_SIGNATURE_VERIFIED\nPG1292 STAGE FULL_CANDIDATE_BOM_VERIFIED\nPG1507_DONE publicationOnlyRecovered=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false\n'
def main():
    entry=inspect.getsource(previous.main)
    for old,new in [('pg1495-publication-recovery-once-v2','pg1507-publication-recovery-once-v3'),('PG1495-publication-recovery-once-v2','PG1507-publication-recovery-once-v3'),('pg1493-publication-recovery-frozen-v2.safe.json','pg1505-publication-recovery-frozen-v3.safe.json'),('pg1493-publication-only-tools-v2','pg1505-publication-only-tools-v3'),('Pg1493PublicationOnlyRecovery','Pg1505PublicationOnlyRecovery')]:
        if old not in entry:raise ValueError('new only current recovery actor binding refused')
        entry=entry.replace(old,new)
    ns={**previous.__dict__,'OUTNAME':OUTNAME,'valid_receipt':valid_receipt}
    exec(compile(entry,'<new once current recovery transport>','exec'),ns);return ns['main']()
if __name__=='__main__':raise SystemExit(main())
