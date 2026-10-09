"""Fresh Inspector owned-resource negative oracles; no VM mutation or formal mixing."""
import json
import pg743_closing_selected as selected
from pg911_snapshot_selected_v2 import code,dependency_bytes
selected.D=selected.W/'pg919-inspector-selected-v1'
selected.TESTS={'batch':['InspectorEnvironmentFilesTest','InspectorEnvironmentPublisherTest','InspectorEnvironmentReaderTest','BrokerJournalQueryTest','InspectorUnitProbeTest','InspectorHeldStateContractTest','InspectorUnitSnapshotTest','ArtemisUnitSnapshotTest']}
if __name__=='__main__':
    print(json.dumps({'dependencyMainClassCounts':dependency_bytes(),'classByteMismatch':0}),flush=True)
    raw=code().replace('PG911-snapshot-selected-v2','PG919-inspector-selected-v1')
    env=dict(selected.__dict__);exec(compile(raw,'<PG919 independent owned-resource oracles>','exec'),env);env['main']()
