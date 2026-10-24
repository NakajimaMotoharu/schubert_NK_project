"""New dependency discovery: imported public test BOM needed for Maven descriptor resolution only."""
from pathlib import Path
import json
import pg8240_prometheus_maven_coordinates as prep
from host_tool_invocation import capture, verify

if __name__ == '__main__':
    invocation = capture(Path(__file__))
    prep.SLOT = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg8243-prometheus-bom-prepare-v1')
    prep.OUT = prep.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8243-prometheus-bom-prepare-v1'
    prep.SLOT.mkdir(exist_ok=False)
    prep.OUT.mkdir(exist_ok=False)
    rows = prep.parent(('org.junit', 'junit-bom', '6.1.0'))
    terminals = list(prep.SLOT.glob('*.exit.safe.json'))
    assert len(rows) == 1 and len(terminals) == 2
    verify(invocation)
    value = dict(status='IMPORTED_DESCRIPTOR_BOM_PREPARED_NOT_TEST_RUNTIME_CHANGE', entries=rows, publicArtifactDownloads=len(terminals), productionPT=0, targetActions=0, vendorSignatureAvailable=False, invocation=invocation, initialCompile='PG8242 failed dependency collection, PT0; immutable evidence retained')
    prep.save(prep.SLOT / 'manifest.json', value)
    prep.save(prep.OUT / 'manifest.json', value)
    print(json.dumps(dict(status=value['status'], manifestSha256=prep.sha(prep.OUT / 'manifest.json'))))
