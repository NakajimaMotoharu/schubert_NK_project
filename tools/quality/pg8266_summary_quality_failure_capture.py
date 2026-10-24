"""Preserve already returned failed post evidence, no rerun or source transfer."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture, verify

if __name__ == '__main__':
    invocation = capture(Path(__file__))
    slot = host.W / 'pg8264-summary-encoder-post-v1'
    out = host.BASE / 'PG8266-summary-quality-failure-v1'
    raw = host.W / 'pg8262-summary-encoder-host-v1/manifest.safe.json'
    assert host.sha(raw) == 'c9e292a3d79d9bc1de92897465200593f773bd73db88dca5a28a3b5568dc954e'
    document = ET.parse(slot / 'static-target/spotbugsXml.xml').getroot()
    bugs = document.findall('.//BugInstance')
    assert len(bugs) == 1 and bugs[0].get('type') == 'FE_FLOATING_POINT_EQUALITY' and not document.findall('.//MissingClass')
    stages = {p.name: json.loads(p.read_text()) for p in slot.glob('*-exit.safe.json')}
    assert len(stages) == 5 and stages['audit-run-exit.safe.json']['actualExit'] == 0
    assert stages['pmd-exit.safe.json']['actualExit'] == 4 and stages['checkstyle-exit.safe.json']['actualExit'] == 0 and stages['spotbugs-exit.safe.json']['actualExit'] == 1
    files = {str(p.relative_to(slot)): host.sha(p) for p in slot.rglob('*') if p.is_file()}
    verify(invocation)
    out.mkdir(exist_ok=False)
    value = dict(status='ORIGINAL_FAILED_QUALITY_POST_PRESERVED_NOT_ACCEPTED', source='b978c6832fe07ec65c162ab90d8bfe0bbddb8034', originalRawSha256=host.sha(raw), originalPostToolSource='5eac9297a', outerExitObserved=1, outerExitEvidence='original tool result session19615, no reconstructed terminal timestamp', stages=stages, files=files, findings=[dict(bugs[0].attrib)], missingClasses=0, currentSourceSuccessTransferred=False, qualificationAccepted=False, originalSelectedPT=58, originalSuites=5, productPTExecutedHere=0, invocation=invocation, bug='BUG-1695')
    host.write(out / 'manifest.json', value)
    print(json.dumps(dict(status=value['status'], manifestSha256=host.sha(out / 'manifest.json'))))
