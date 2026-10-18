import pg5332_service_resources_selected as entry
import pg5281_factory_finish as finish
from pg5334_service_resources_bytecode import SOURCE


if __name__=='__main__':
    finish.classify_current(entry=entry,source=SOURCE,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5328-scope-classification-cgroup-owner-v1/manifest.json',
        previous_sha='19dcae1fb936860944fd934bb3acc83933a41924c6a5d26673a18f01f47a59c1',
        previous_source='82426a6b20b83855da4a46f134d8f15981914669',
        qualified_ref='018_NK-OPS-001/evidence/provisional/pg5332-service-resources-green-v1-metadata-v2/manifest.json',
        tests=1090,suites=132,counts={'FIXED_LIMITED':203,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':33},
        out_name='PG5338-scope-classification-service-resources-v1',
        extra={'additionalFactoryDefectsOutsideOriginal':2,'additionalFactoryFixedLimited':2,
            'additionalFactoryFormalFixed':0,'extraReadonlyCandidatesStillPending':4})
