"""Requalify original237 at handoff source, zero candidate closure until clients change."""
import json
import os
import pg5261_scope_inventory_continue as carry
import pg5296_handoff_selected as entry
from pg5298_handoff_bytecode import SOURCE


if __name__=='__main__':
    value,proof=carry.continue_current(root=entry.selected.ROOT,sha=entry.selected.sha,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5294-scope-classification-morning-launch-v1/manifest.json',
        previous_sha='b2ec6892af7c9ddc3d34ab25978d8edd6e0b7bba9b900aa36289dd4e8232578d',
        previous_source='6f8d42065ce19f79edc8e54dd99f991eda1a06a4',source=SOURCE,
        qualified_ref='018_NK-OPS-001/evidence/provisional/pg5296-handoff-green-v1-metadata-v2/manifest.json',
        tests=1011,suites=124,new_files=set(),
        expected_counts={'FIXED_LIMITED':190,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':46})
    value.update(commonHandoffOnly=True,original237ClosedDelta=0,scopeFourCounters=proof['scopeFourCounters'],
        additionalFactoryDefectsOutsideOriginal=2,additionalFactoryFixed=0)
    out=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5302-scope-classification-handoff-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'counts':value['classificationCounts'],'sha256':entry.selected.sha(out/'manifest.json')}))
