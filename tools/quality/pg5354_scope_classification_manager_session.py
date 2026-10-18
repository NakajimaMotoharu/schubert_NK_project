import pg5348_manager_session_selected as entry
import pg5281_factory_finish as finish
from pg5350_manager_session_bytecode import SOURCE,RUN


if __name__=='__main__':
    finish.classify_current(entry=entry,source=SOURCE,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5346-scope-classification-service-resources-v1/manifest.json',
        previous_sha='a26115832f2785548fb7287b03a31d772fbcb62fe732e14b5ec6cf85e55ef1af',
        previous_source='7aa3ab90c26701a6cce96fe92151e85a802fb3cb',
        qualified_ref='018_NK-OPS-001/evidence/provisional/'+RUN+'-metadata-v2/manifest.json',
        tests=1092,suites=132,counts={'FIXED_LIMITED':204,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':32},
        out_name='PG5354-scope-classification-manager-session-v1',
        extra={'additionalFactoryFixedLimited':2,'additionalFactoryFormalFixed':0,'extraReadonlyCandidatesStillPending':4})
