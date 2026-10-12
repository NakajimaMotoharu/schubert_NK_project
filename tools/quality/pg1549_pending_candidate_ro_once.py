"""One fresh candidate-only hostRO; existing failed original/current unchanged."""
import inspect
import pg1481_partial_original_profile as prior
from pg1546_pending_candidate_ro_sources import CLASS,TOOLS,SAVE

def valid_receipt(data):
    return type(data)is bytes and data==b'PG1292 STAGE PINNED_SIGNATURE_VERIFIED\nPG1292 STAGE FULL_CANDIDATE_BOM_VERIFIED\nPG1544 STAGE FIXED_CANDIDATE_HOST_RO\nPG1544 STAGE PINNED_SIGNATURE_VERIFIED\nPG1544 STAGE FULL_CANDIDATE_BOM_VERIFIED\nPG1549_DONE candidateHostRo=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false\n'

def source():
    raw=inspect.getsource(prior.main)
    for old,new in [('pg1481-partial-original-profile-v1',SAVE),('PG1481-partial-original-profile-v1','PG1549-pending-candidate-ro-v1'),('pg1478-partial-profile-frozen-v1.safe.json','pg1547-pending-candidate-ro-frozen-v1.safe.json'),('pg1478-partial-original-tools-v1',TOOLS),('Pg1478PartialOriginalProfile',CLASS),("'profile']","'prepare-ro']"),('profileTimingQualificationPending','candidateRoIndependentClosingPending')]:
        if old not in raw:raise ValueError('fixed candidate RO once boundary refused')
        raw=raw.replace(old,new)
    compile(raw,'<once candidate RO framing>', 'exec');return raw

def main():
    ns={**prior.__dict__,'OUTNAME':'pg1548-pending-ro-stage-v1','valid_receipt':valid_receipt};exec(compile(source(),'<once current-owned candidate RO>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
