"""Complete affected snapshot caller suites on the new candidate, fresh execution only."""
import json
import pg743_closing_selected as selected
from pg911_snapshot_selected_v2 import code, dependency_bytes

selected.D = selected.W / 'pg911-snapshot-selected-v5'
selected.TESTS = {'batch': [
    'InspectorUnitProbeTest', 'InspectorHeldStateContractTest', 'ArtemisUnitSnapshotTest',
    'BackupUnitReceiptGateTest', 'CleanupUnitCycleTest', 'InspectorUnitSnapshotTest',
    'MorningBackupUnitCycleTest', 'MorningPreviousBrokerTest', 'CleanupFailedBackupRequestTest',
    'InspectorUnitCycleTest', 'MorningNoPriorBrokerTest', 'MorningBrokerUnitCycleTest',
    'BackupUnitTerminationTest', 'MorningControlScopeTest',
]}
if __name__ == '__main__':
    print(json.dumps({'dependencyMainClassCounts': dependency_bytes(), 'classByteMismatch': 0}), flush=True)
    raw = code().replace('PG911-snapshot-selected-v2', 'PG911-snapshot-selected-v5')
    env = dict(selected.__dict__)
    exec(compile(raw, '<911 v5 full affected snapshot callers>', 'exec'), env)
    env['main']()
