"""Fixed public inputs for the independent snapshot whole-program qualification."""
import g07_host_class_provenance_inputs as data

SOURCE = '0061d178cda80c2ce3926290619c64db125dbcfc'
PREFIX = 'snapshot-program'
NORMAL_NUMBER = 13832
STATIC_NUMBER = 13836
NORMAL = data.BASE/'PG13832-snapshot-program-six-compile-v1'
NORMAL_SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13832-snapshot-program-six-compile-v1'
TEST_ROOT = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/'
PINS = {
    'InspectorUnitSnapshotTest':'edf0ce67d649d340e2e61907cc8228cd9c44fe08a21a9f011d81cdcbef4d1a63',
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
