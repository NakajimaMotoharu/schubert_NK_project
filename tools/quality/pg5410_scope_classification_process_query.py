import pg5404_process_query_selected as entry
import pg5281_factory_finish as finish
from pg5406_process_query_bytecode import SOURCE,RUN


if __name__=='__main__':
    finish.classify_current(entry=entry,source=SOURCE,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5402-scope-classification-archive-complete-v1/manifest.json',
        previous_sha='ae607bad53d148184b7a92f4161b76a05c4259959e6e93e0f748fe09817fed28',
        previous_source='60bc8f54b154e82c16ad3a32a71143d7ca80affe',
        qualified_ref='018_NK-OPS-001/evidence/provisional/'+RUN+'-metadata-v2/manifest.json',
        tests=1164,suites=137,counts={'FIXED_LIMITED':236,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':0},
        out_name='PG5410-scope-classification-process-query-v1',
        extra={'additionalFactoryFixedLimited':4,'additionalFactoryFormalFixed':0,
            'extraReadonlyCandidatesStillPending':4,'physicalMain':767,'netMainGrowth':2})
