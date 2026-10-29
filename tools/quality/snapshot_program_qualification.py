"""Fixed public inputs for the independent snapshot whole-program qualification."""
import g07_host_class_provenance_inputs as data

SOURCE = '23582a606b50efbea63442b7a8487d1c9f2e7035'
PREFIX = 'snapshot-program'
NORMAL_NUMBER = 13812
STATIC_NUMBER = 13816
NORMAL = data.BASE/'PG13812-snapshot-program-six-compile-v1'
NORMAL_SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13812-snapshot-program-six-compile-v1'
TEST_ROOT = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/'
PINS = {
    'InspectorUnitSnapshotTest':'910a28246caf9b15942a4a5da52ad3ba1128b8193e7cbae8d250ac6c230562a3',
    'InspectorHeldStateContractTest':'15f183d2a47186954381876bc2a8e9cbf9505c3bdda08f6e5dca242e608f6b66',
    'ArtemisUnitSnapshotTest':'968b2e8371cd008c36729e251cc406eea6b48c305222b0dbeb8de8038a5bbcd0',
}
COUNTS = {'InspectorUnitSnapshotTest':10,'InspectorHeldStateContractTest':9,'ArtemisUnitSnapshotTest':4}
CONFIG = 'src/deployment/systemd/artemis.service'
CONFIG_SHA = '1b8fe8eaab683ac658bfe8c23816e709725431a0a2b80816bba5449d129c5266'

def out(config,number):
    return NORMAL if number == NORMAL_NUMBER else data.BASE/('PG'+str(number)+'-'+config.PREFIX+'-v1')

def normal():
    path = NORMAL/'manifest.json'
    pin = data.sha(path.read_bytes())
    result = data.read_checked(path,pin)
    assert result['source'] == SOURCE and result['actualExit'] == result['testsExecuted'] == 0
    assert data.sha((NORMAL_SLOT/'manifest.safe.json').read_bytes()) == pin
    return result,pin
