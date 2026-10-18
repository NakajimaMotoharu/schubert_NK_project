import pg5380_nss_root_query_selected as entry
import pg5281_factory_finish as finish
from pg5382_nss_root_query_bytecode import SOURCE,RUN


if __name__=='__main__':
    finish.classify_current(entry=entry,source=SOURCE,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5378-scope-classification-ffm-progress-v1/manifest.json',
        previous_sha='2939a23195a187c8d492a2e219d64206d3b6cdc166c9db455dbd261d95757bd7',
        previous_source='fceffefd6639ae0b217565dc0acdf0d2e0a2a6fe',
        qualified_ref='018_NK-OPS-001/evidence/provisional/'+RUN+'-metadata-v2/manifest.json',
        tests=1122,suites=133,counts={'FIXED_LIMITED':217,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':19},
        out_name='PG5386-scope-classification-nss-root-query-v1',
        extra={'additionalFactoryFixedLimited':4,'additionalFactoryFormalFixed':0,
            'extraReadonlyCandidatesStillPending':4})
