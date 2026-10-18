import json
import pg5304_permit_intent_selected as entry
import pg5281_factory_finish as finish
from pg5306_permit_intent_bytecode import SOURCE


if __name__=='__main__':
    path=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5306-permit-intent-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    if proof['source']!=SOURCE or proof['actualExit']!=0 or proof['extraDirectoryOwnerFactories']!=2:
        raise ValueError('actual entire owner chain source proof first')
    finish.classify_current(entry=entry,source=SOURCE,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5302-scope-classification-handoff-v1/manifest.json',
        previous_sha='867569d02c50df76164939e0e5998403c2ea542985e3217725517efff884f785',
        previous_source='5eb1d4c44650b79aa8983f044531b3e3e22e214e',
        qualified_ref='018_NK-OPS-001/evidence/provisional/pg5304-permit-intent-green-v1-metadata-v2/manifest.json',
        tests=1038,suites=126,counts={'FIXED_LIMITED':194,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':42},
        out_name='PG5310-scope-classification-permit-intent-v1',
        extra={'additionalFactoryDefectsOutsideOriginal':2,'additionalFactoryFixedLimited':2,
            'additionalFactoryFormalFixed':0,'additionalFactoryProofSha256':entry.selected.sha(path),
            'additionalFactoryFiles':['BackupStartIntentFiles.create','BackupStartIntentFiles.createPublication'],
            'manualCreateServiceOpcodesAndHandlersUnchanged':True,'extraReadonlyCandidatesStillPending':4})
