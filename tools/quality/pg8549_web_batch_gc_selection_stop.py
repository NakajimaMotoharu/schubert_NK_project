"""Preserve actual unrun foreign-suite launcher failure, never manufacture original PT success."""
import datetime
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture, verify

SLOT = host.W / 'pg8548-web-batch-gc-host-v1'
OUT = host.BASE / 'PG8549-web-batch-gc-selection-stop-v1'

def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    begin = json.loads((SLOT / 'begin.safe.json').read_text())
    stages = {n: json.loads((SLOT / (n + '-exit.safe.json')).read_text()) for n in ('fresh-test-compile', 'selected-junit')}
    assert begin['source'] == '623be8eeaf078f85cfa5682dced7a3b2e21a2b49'
    assert stages['fresh-test-compile']['actualExit'] == 0 and stages['selected-junit']['actualExit'] == 1
    xmls = list((SLOT / 'xml').glob('TEST-*.xml'))
    assert len(xmls) == 1
    root = ET.parse(xmls[0]).getroot()
    assert root.get('name') == 'dev.codex.schubert.nk.api.monitoring.ApiGcMetricRegistrationTest' and root.get('tests') == '0'
    helper = host.ROOT / 'tools/quality/architecture/WebBatchGcMetricsJunitLauncher.java'
    assert host.sha(helper) == begin['testSourceHashes'][str(helper)]
    files = [SLOT / 'begin.safe.json', SLOT / 'jacoco.exec', SLOT / 'xml/summary.safe.txt', xmls[0]]
    files += [SLOT / (name + suffix) for name in stages for suffix in ('-begin.safe.json', '-process.safe.json', '-exit.safe.json', '.log')]
    verify(invocation)
    value = dict(actualExit=1, source=begin['source'], timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), invocation=invocation, bug='BUG-1707', rollout='YKT-1458', originalBegin=begin, originalStages=stages, expectedTests=28, actualTests=0, testStatus='UNRUN_NOT_PASS', evidenceHashes={str(p): host.sha(p) for p in files}, originalLauncher=helper.read_text(), originalLauncherSha256=host.sha(helper), productTestsExecutedByPreservation=0, whole451Accepted=False, formalUpdated=False, newAccepted=0, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(preserved=True, actualTests=0, originalJunitExit=1, manifestSha256=host.sha(OUT / 'manifest.json'))))

if __name__ == '__main__':
    main()
