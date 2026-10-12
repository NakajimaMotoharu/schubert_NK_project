"""One new code-only publication; fixed old classpath, no epoch or runtime start."""
import inspect
import pg1481_partial_original_profile as prior
from pg1553_pending_publication_java import CLASS,TOOLS,SAVE

def valid_receipt(data):
    return type(data)is bytes and data==b'PG1292 STAGE PINNED_SIGNATURE_VERIFIED\nPG1292 STAGE FULL_CANDIDATE_BOM_VERIFIED\nPG1544 STAGE PINNED_SIGNATURE_VERIFIED\nPG1544 STAGE FULL_CANDIDATE_BOM_VERIFIED\nPG1556_DONE pendingCodeOnly=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false\n'

def source():
    raw=inspect.getsource(prior.main)
    for old,new in [('pg1481-partial-original-profile-v1',SAVE),('PG1481-partial-original-profile-v1','PG1556-pending-publication-v1'),('pg1478-partial-profile-frozen-v1.safe.json','pg1555-pending-publication-frozen-v1.safe.json'),('pg1478-partial-original-tools-v1',TOOLS),('Pg1478PartialOriginalProfile',CLASS),("'profile']","'activate']"),('profileTimingQualificationPending','codeOnlyIndependentClosingPending'),('/opt/schubert-nk/current/','/opt/schubert-nk/releases/0.1.0-PG1292/')]:
        if old not in raw:raise ValueError('fixed publication once boundary refused')
        raw=raw.replace(old,new)
    # Explicitly distinguish code publication from epoch/DB/business writes.
    raw=raw.replace("'businessMutations0':True","'epochDbBusinessWrites0':True,'codeApprovalCurrentOnly':True")
    compile(raw,'<once partial publication framing>','exec');return raw

def main():
    ns={**prior.__dict__,'OUTNAME':'pg1557-pending-publication-stage-v1','valid_receipt':valid_receipt};exec(compile(source(),'<once current-owned no-epoch publication>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
