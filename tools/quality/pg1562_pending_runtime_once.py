"""One fresh fixed runtime preparation, start/epoch/business writes0."""
import inspect
import pg1481_partial_original_profile as prior
from pg1559_pending_runtime_sources import CLASS,TOOLS,SAVE,SOURCE

def valid_receipt(data):
    return type(data)is bytes and data==b'PG1544 STAGE PINNED_SIGNATURE_VERIFIED\nPG1544 STAGE FULL_CANDIDATE_BOM_VERIFIED\nPG1562_DONE onceRuntimePrepared=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false\n'

def source():
    raw=inspect.getsource(prior.main)
    for a,b in [('pg1481-partial-original-profile-v1',SAVE),('PG1481-partial-original-profile-v1','PG1562-pending-runtime-v1'),('pg1478-partial-profile-frozen-v1.safe.json','pg1560-pending-runtime-frozen-v1.safe.json'),('pg1478-partial-original-tools-v1',TOOLS),('Pg1478PartialOriginalProfile',CLASS),("'profile']","'prepare']"),('profileTimingQualificationPending','runtimeIndependentClosingPending'),('/opt/schubert-nk/current/','/opt/schubert-nk/releases/0.1.0-PG1544/'),('769ddb15cd735c25fef581b5f9850ef9d0053c0f',SOURCE)]:
        if a not in raw:raise ValueError('fixed runtime once boundary refused')
        raw=raw.replace(a,b)
    compile(raw,'<once new current runtime framing>','exec');return raw

def main():
    ns={**prior.__dict__,'OUTNAME':'pg1561-pending-runtime-stage-v1','valid_receipt':valid_receipt};exec(compile(source(),'<once owned runtime preparation>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
