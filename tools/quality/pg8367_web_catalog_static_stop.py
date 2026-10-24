"""Preserve original14 success and actual PMD failure before repair, no product replay."""
import datetime
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture, verify

OUT = host.BASE / 'PG8367-web-catalog-static-stop-v1'
SLOT = host.W / 'pg8366-web-catalog-post-v1'


def main():
    invocation = capture(Path(__file__))
    normal = host.BASE / 'PG8362-web-catalog-six-compile-v1/manifest.json'
    original = host.BASE / 'PG8364-web-catalog-host-v1/manifest.json'
    assert not OUT.exists() and host.sha(normal) == '51c75e43da20b8089a81fbc24dc7e4d5d797e4f8d511225ab0c68db2b14f7e96' and host.sha(original) == '56f70b238d9cb4971281bea0809a1ad932930f023891dc62db8dd77b274e2ef3'
    raw = json.loads(original.read_text())
    assert raw['actualExit'] == 0 and raw['begin']['expectedTests'] == 14 and len(raw['cases']) == 14 and all(r['result'] == 'PASS' for r in raw['cases'])
    files = ('pmd.xml', 'pmd-exit.safe.json', 'audit-run.stdout.log', 'audit-run-exit.safe.json')
    pins = {name: host.sha(SLOT / name) for name in files}
    pmd = json.loads((SLOT / 'pmd-exit.safe.json').read_text())
    audit = json.loads((SLOT / 'audit-run-exit.safe.json').read_text())
    rows = ET.parse(SLOT / 'pmd.xml').getroot().findall('.//{*}violation')
    assert pmd['actualExit'] == 4 and audit['actualExit'] == 0 and len(rows) == 1 and rows[0].get('rule') == 'AvoidDuplicateLiterals'
    verify(invocation)
    value = dict(actualExit=1, source='7ca3acb10533696798a368321032b4bbaeb7fd86', invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), bug='BUG-1700', rollout='YKT-1451', originalManifestSha256=host.sha(original), normalManifestSha256=host.sha(normal), originalTests=14, originalSuites=1, originalProductPtExit=0, postAccepted=False, failedStatic='pmd', staticReceipt=pmd, auditReceipt=audit, evidenceHashes=pins, rawFindings=[dict(row.attrib, message=' '.join(''.join(row.itertext()).split())) for row in rows], unrun=['checkstyle', 'spotbugs', 'whole451'], productTestsExecutedByPreservation=0, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, formalUpdated=False, newAccepted=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(preserved=True, originalTests=14, actualPostFailure=True, staticFindings=1, productTestsExecuted=0, manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
