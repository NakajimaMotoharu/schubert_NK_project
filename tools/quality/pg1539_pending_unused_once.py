"""One reserved failed-partial unused placement; no current switch or Root start."""
import inspect
import json
from pg1446_current_cold_stage import W
import pg1481_partial_original_profile as prior
from pg1536_pending_candidate_sources import CLASS, TOOLS, SAVE

def valid_receipt(data):
    return type(data)is bytes and data==b'PG1292 STAGE PINNED_SIGNATURE_VERIFIED\nPG1292 STAGE FULL_CANDIDATE_BOM_VERIFIED\nPG1539_DONE unusedPlacement=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false\n'

def source():
    raw=inspect.getsource(prior.main)
    for old,new in [('pg1481-partial-original-profile-v1',SAVE),('PG1481-partial-original-profile-v1','PG1539-pending-unused-placement-v1'),('pg1478-partial-profile-frozen-v1.safe.json','pg1537-pending-unused-frozen-v1.safe.json'),('pg1478-partial-original-tools-v1',TOOLS),('Pg1478PartialOriginalProfile',CLASS),("'profile']","'place']"),('profileTimingQualificationPending','unusedPlacementIndependentClosingPending')]:
        if old not in raw:raise ValueError('fixed once partial placement boundary refused')
        raw=raw.replace(old,new)
    compile(raw,'<once partial-original unused placement>', 'exec')
    return raw

def main():
    input_stage=json.loads((W/'pg1538-signed-input-stage-v1.safe.json').read_bytes())
    if input_stage['actualExit']!=0 or input_stage['candidatePlacementIssued'] is not False:
        raise ValueError('new-only signed input stage required')
    ns={**prior.__dict__,'OUTNAME':'pg1538-pending-unused-stage-v1','valid_receipt':valid_receipt}
    exec(compile(source(),'<once authenticated partial placement transport>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
