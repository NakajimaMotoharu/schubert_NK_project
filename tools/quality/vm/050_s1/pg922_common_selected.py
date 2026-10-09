"""Bounded common bootstrap API negatives; unchanged production, new test source only."""
import json
import pg743_closing_selected as selected
from pg911_snapshot_selected_v2 import code,dependency_bytes
selected.D=selected.W/'pg922-common-selected-v1'
selected.TESTS={'bootstrap':['FixedNativeCoverageCheckpointTest','FixedNativeCoverageProfileTest','FixedNativeCoverageStopHoldTest','ChildBrokerTest','ChildCaddyTest','ChildStartupContextTest']}
if __name__=='__main__':
    print(json.dumps({'dependencyMainClassCounts':dependency_bytes(),'classByteMismatch':0}),flush=True)
    raw=code().replace("'src/schubert-nk-batch',", "'src/schubert-nk-bootstrap',").replace('PG911-snapshot-selected-v2','PG922-common-selected-v1')
    env=dict(selected.__dict__);exec(compile(raw,'<PG922 closed common negatives>','exec'),env);env['main']()
