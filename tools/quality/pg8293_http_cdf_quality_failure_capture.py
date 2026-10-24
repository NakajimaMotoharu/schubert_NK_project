"""Preserve already returned failed post evidence, no rerun or source transfer."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture, verify

if __name__ == '__main__':
    invocation = capture(Path(__file__))
    slot = host.W / 'pg8292-http-cdf-fixed-post-v1'
    out = host.BASE / 'PG8293-http-cdf-quality-failure-v1'
    raw = host.W / 'pg8290-http-cdf-fixed-host-v1/manifest.safe.json'
    assert host.sha(raw) == 'ea4d044940f8d65f2f22f0e012c351927750337947dfc2f00dfbd191b0ea8173'
    document = ET.parse(slot / 'static-target/spotbugsXml.xml').getroot()
    bugs = document.findall('.//BugInstance')
    assert len(bugs) == 2 and all(b.get('type') == 'CWO_CLOSED_WITHOUT_OPENED' for b in bugs) and not document.findall('.//MissingClass')
    stages = {p.name: json.loads(p.read_text()) for p in slot.glob('*-exit.safe.json')}
    assert len(stages) == 5 and stages['audit-run-exit.safe.json']['actualExit'] == 0
    assert stages['pmd-exit.safe.json']['actualExit'] == 0 and stages['checkstyle-exit.safe.json']['actualExit'] == 0 and stages['spotbugs-exit.safe.json']['actualExit'] == 1
    files = {str(p.relative_to(slot)): host.sha(p) for p in slot.rglob('*') if p.is_file()}
    verify(invocation)
    out.mkdir(exist_ok=False)
    value = dict(status='ORIGINAL_FAILED_QUALITY_POST_PRESERVED_NOT_ACCEPTED', source='f1a898b58a893837582b06861b33863407792139', originalRawSha256=host.sha(raw), originalPostToolSource='2684b135d', outerExitObserved=1, outerExitEvidence='original tool result session61435, no reconstructed terminal timestamp', stages=stages, files=files, findings=[dict(b.attrib) for b in bugs], missingClasses=0, currentSourceSuccessTransferred=False, qualificationAccepted=False, originalSelectedPT=32, originalSuites=4, productPTExecutedHere=0, invocation=invocation, bug='BUG-1696')
    host.write(out / 'manifest.json', value)
    print(json.dumps(dict(status=value['status'], manifestSha256=host.sha(out / 'manifest.json'))))
