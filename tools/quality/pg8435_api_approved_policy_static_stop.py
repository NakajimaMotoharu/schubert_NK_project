"""Preserve original94 success and actual PMD failure before repair, no product replay."""
import datetime
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture, verify

OUT = host.BASE / 'PG8435-api-approved-policy-static-stop-v1'
SLOT = host.W / 'pg8434-api-approved-policy-post-v1'


def main():
    invocation = capture(Path(__file__))
    normal = host.BASE / 'PG8430-api-approved-policy-six-compile-v1/manifest.json'
    original = host.BASE / 'PG8432-api-approved-policy-host-v1/manifest.json'
    assert not OUT.exists() and host.sha(normal) == '65b56cec716e91333cd067559f0f6c20b01963ccbf899ee29d41bdae38683744' and host.sha(original) == '3ef9e95a693b9085b39e4bf61ed0bd6e563f78c718b0a02d3aa6dde8cb9e996a'
    raw = json.loads(original.read_text())
    assert raw['actualExit'] == 0 and raw['begin']['expectedTests'] == 94 and len(raw['cases']) == 94 and all(r['result'] == 'PASS' for r in raw['cases'])
    files = ('pmd.xml', 'pmd-exit.safe.json', 'audit-run.stdout.log', 'audit-run-exit.safe.json')
    pins = {name: host.sha(SLOT / name) for name in files}
    pmd = json.loads((SLOT / 'pmd-exit.safe.json').read_text())
    audit = json.loads((SLOT / 'audit-run-exit.safe.json').read_text())
    rows = ET.parse(SLOT / 'pmd.xml').getroot().findall('.//{*}violation')
    assert pmd['actualExit'] == 4 and audit['actualExit'] == 0 and len(rows) == 4 and sorted(r.get('rule') for r in rows) == ['AvoidFieldNameMatchingMethodName'] * 3 + ['AvoidLiteralsInIfCondition']
    verify(invocation)
    value = dict(actualExit=1, source='a79d0ae0d88c265b4e26a545318399b74d98d97e', invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), bug='BUG-1703', rollout='YKT-1454', originalManifestSha256=host.sha(original), normalManifestSha256=host.sha(normal), originalTests=94, originalSuites=7, originalProductPtExit=0, postAccepted=False, failedStatic='pmd', staticReceipt=pmd, auditReceipt=audit, evidenceHashes=pins, rawFindings=[dict(row.attrib, message=' '.join(''.join(row.itertext()).split())) for row in rows], unrun=['checkstyle', 'spotbugs', 'whole451'], productTestsExecutedByPreservation=0, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, formalUpdated=False, newAccepted=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(preserved=True, originalTests=94, actualPostFailure=True, staticFindings=4, productTestsExecuted=0, manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()

