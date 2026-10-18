"""Same four sites requalified, not four additional fixed sites after a coverage repair."""
import json
import os
import pg5332_service_resources_selected as entry
import pg5261_scope_inventory_continue as carry
from pg5342_service_resources_bytecode import SOURCE,RUN


if __name__=='__main__':
    value,proof=carry.continue_current(root=entry.selected.ROOT,sha=entry.selected.sha,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5338-scope-classification-service-resources-v1/manifest.json',
        previous_sha='f03531b33dc3823d9041b2f0760c2c3539b2ccad68f3aca73e232e68c47ea069',
        previous_source='96f743eac9856e732ef5e36153adcc47a23b17fb',source=SOURCE,
        qualified_ref='018_NK-OPS-001/evidence/provisional/'+RUN+'-metadata-v2/manifest.json',
        tests=1090,suites=132,new_files=set(),
        expected_counts={'FIXED_LIMITED':203,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':33})
    value.update(serviceFourCounters=proof['serviceFourCounters'],additionalFactoryFixedLimited=2,
        additionalFactoryFormalFixed=0,extraReadonlyCandidatesStillPending=4,additionalSitesCredited=0)
    out=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5346-scope-classification-service-resources-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with (out/'manifest.json').open('x') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'counts':value['classificationCounts'],'sha256':entry.selected.sha(out/'manifest.json')}))
