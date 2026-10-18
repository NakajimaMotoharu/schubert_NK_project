import pg5390_archive_pipeline_selected as entry
import pg5281_factory_finish as finish
from pg5392_archive_pipeline_bytecode import SOURCE,RUN


if __name__=='__main__':
    finish.classify_current(entry=entry,source=SOURCE,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5386-scope-classification-nss-root-query-v1/manifest.json',
        previous_sha='18686b080058b456534cc0c427ff9154d87277f492411d06e14c2aff9e473a06',
        previous_source='d3f618962cc3a0297c818cd4890698c2269a0f5f',
        qualified_ref='018_NK-OPS-001/evidence/provisional/'+RUN+'-metadata-v2/manifest.json',
        tests=1138,suites=134,counts={'FIXED_LIMITED':224,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':12},
        out_name='PG5396-scope-classification-archive-pipeline-v1',
        extra={'additionalFactoryFixedLimited':4,'additionalFactoryFormalFixed':0,
            'extraReadonlyCandidatesStillPending':4,'physicalMain':765,'netMainGrowth':1})
