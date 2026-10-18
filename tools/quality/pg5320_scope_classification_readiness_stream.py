import pg5314_readiness_stream_selected as entry
import pg5281_factory_finish as finish
from pg5316_readiness_stream_bytecode import SOURCE


if __name__=='__main__':
    finish.classify_current(entry=entry,source=SOURCE,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5310-scope-classification-permit-intent-v1/manifest.json',
        previous_sha='ddf630179ef6714a69ad795a4c3f6e7414ccd8f8e0780a1fb0453aed33fe5e49',
        previous_source='c29752dbe4de7b24ee92bfa4fb71f2e164c16515',
        qualified_ref='018_NK-OPS-001/evidence/provisional/pg5314-readiness-stream-green-v1-metadata-v2/manifest.json',
        tests=1068,suites=129,counts={'FIXED_LIMITED':197,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':39},
        out_name='PG5320-scope-classification-readiness-stream-v1',
        extra={'additionalFactoryDefectsOutsideOriginal':2,'additionalFactoryFixedLimited':2,
            'additionalFactoryFormalFixed':0,'additionalFactoryProofRef':'PG5306 cd4c094d/1086; both current files byte-identical',
            'additionalFactoryFiles':['BackupStartIntentFiles.create','BackupStartIntentFiles.createPublication'],
            'extraReadonlyCandidatesStillPending':4})
