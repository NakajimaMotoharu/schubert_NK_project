"""Preserve failed normal test-compile and diagnose only the new API JVM Main, never Root11."""
import datetime
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import scoped_prometheus_post as post
from host_tool_invocation import capture, verify

host = post.host
SLOT = host.W / 'pg8475-api-jvm-preflight-v1'
OUT = host.BASE / 'PG8475-api-jvm-preflight-v1'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiJvmMetrics.java'

if __name__ == '__main__':
    invocation = capture(Path(__file__))
    failed = host.BASE / 'PG8474-api-jvm-six-compile-v1/manifest.json'
    assert host.sha(failed) == '8da752f99d57d9ad1d749c8b0b1189e97c196d098983d8e60884035cd1d3745d'
    raw = json.loads(failed.read_text())
    assert raw['actualExit'] == raw['terminal']['actualExit'] == 1 and raw['testsExecuted'] == 0
    normal_slot = host.W / 'pg8474-api-jvm-six-compile-v1'
    text = (normal_slot / 'maven.log').read_text()
    assert host.sha(normal_slot / 'maven.log') == raw['terminal']['logSha256']
    assert text.count('explicit call to close() on an auto-closeable resource') == 1
    assert host.sha(host.ROOT / MAIN) == raw['begin']['inputHashes'][MAIN]
    assert not SLOT.exists() and not OUT.exists()
    SLOT.mkdir()
    post.SLOT = SLOT
    static = host.TC / 'static-gates-20261015'
    cp = os.pathsep.join(str(p) for p in [static / 'record-fix-v1/pmd-record-1298.jar', *sorted((static / 'pmd-bin-7.28.0/lib').glob('*.jar'))])
    receipt, _ = post.step('pmd-diagnostic', [str(host.TC / 'jdk-25.0.4/bin/java'), '-cp', cp, 'net.sourceforge.pmd.cli.PmdCli', 'check', '--dir', str(host.ROOT / MAIN), '--rulesets', str(host.ROOT / 'tools/quality/static/pmd.xml'), '--use-version', 'java-25', '--minimum-priority', '5', '--no-cache', '--format', 'xml', '--report-file', str(SLOT / 'pmd.xml')])
    doc = ET.parse(SLOT / 'pmd.xml').getroot()
    rows = [dict(r.attrib, message=' '.join(''.join(r.itertext()).split())) for r in doc.findall('.//{*}violation')]
    assert not doc.findall('.//{*}error') and receipt['actualExit'] in (0, 4) and not receipt['timedOut']
    verify(invocation)
    OUT.mkdir()
    value = dict(source=raw['source'], timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), actualNormalExit=1, normalManifestSha256=host.sha(failed), normalLogSha256=raw['terminal']['logSha256'], testCompileWarning='explicit close() in try-with-resources fixture', testsExecuted=0, ptStatus='UNRUN_NOT_PASS', mainSourceSha256=host.sha(host.ROOT / MAIN), diagnosticOnly=True, pmdReceipt=receipt, rawFindings=rows, pmdXmlSha256=host.sha(SLOT / 'pmd.xml'), auxClasspathQualified=False, coverageQualified=False, checkstyleExecuted=False, spotbugsExecuted=False, whole451Accepted=False, formalUpdated=False, actualVmActions=0, actualDatabaseActions=0, actualServiceActions=0, invocation=invocation)
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(normalExit=1, testsExecuted=0, rawPmdFindings=rows, manifestSha256=host.sha(OUT / 'manifest.json'))))

