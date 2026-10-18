import pg5322_cgroup_owner_selected as entry
import pg5281_factory_finish as finish
from pg5324_cgroup_owner_bytecode import SOURCE


if __name__=='__main__':
    finish.classify_current(entry=entry,source=SOURCE,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5320-scope-classification-readiness-stream-v1/manifest.json',
        previous_sha='e0ee5c7f6d7f4d29500ace2b60567081a20f093aca3234e438d0fa1c4a645a97',
        previous_source='2a48e4e1b3fc5f90d35f7b8a9ce049947402f1df',
        qualified_ref='018_NK-OPS-001/evidence/provisional/pg5322-cgroup-owner-green-v1-metadata-v2/manifest.json',
        tests=1086,suites=131,counts={'FIXED_LIMITED':199,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':37},
        out_name='PG5328-scope-classification-cgroup-owner-v1',
        extra={'additionalFactoryDefectsOutsideOriginal':2,'additionalFactoryFixedLimited':2,
            'additionalFactoryFormalFixed':0,'additionalFactoryProofRef':'PG5306 cd4c094d/1086; current same byte and current cohort',
            'extraReadonlyCandidatesStillPending':4})
