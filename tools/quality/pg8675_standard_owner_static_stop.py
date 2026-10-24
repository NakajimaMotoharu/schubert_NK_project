"""Preserve original fixed source16/real coverage and PMD3 before repair; no product execution."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

if __name__=='__main__':
    invocation=capture(Path(__file__))
    out=host.BASE/'PG8675-standard-owner-static-stop-v1'
    assert not out.exists()
    run=host.W/'pg8672-api-standard-source-host-v1'
    post=host.W/'pg8674-api-standard-source-post-v1'
    assert host.sha(run/'manifest.safe.json')=='a1bbf084aac789cd9d8ed7c6c9ca975bcc02fe917a127eb8da4651878fe5e781'
    raw=json.loads((run/'manifest.safe.json').read_text())
    assert raw['actualExit']==0 and len(raw['cases'])==16
    pmd=(post/'pmd.xml').read_text()
    found=ET.fromstring(pmd).findall('.//{*}violation')
    assert len(found)==3 and {v.get('method') for v in found}=={'bind','scrape','close'} and all(v.get('rule')=='AvoidSynchronizedAtMethodLevel' for v in found)
    main=host.ROOT/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiStandardMetricSource.java'
    audit=(post/'audit-run.stdout.log').read_text()
    assert 'LINE:0:34' in audit and 'METHOD:0:9' in audit and 'CLASS:0:1' in audit and 'BRANCH:0:19' in audit
    verify(invocation)
    out.mkdir()
    host.write(out/'manifest.json',dict(bug='BUG-1712',ykt='YKT-1463',source=raw['source'],invocation=invocation,originalManifestSha256=host.sha(run/'manifest.safe.json'),originalTests=16,originalExit=0,execSha256=raw['execSha256'],xmlHashes=raw['xmlHashes'],oldMainSha256=host.sha(main),oldMainText=main.read_text(),pmdXml=pmd,pmdReportSha256=host.sha(post/'pmd.xml'),actualAudit=audit,auditSha256=host.sha(post/'audit-run.stdout.log'),staticComplete=False,checkstyle='UNRUN',spotbugs='UNRUN',oldSuccessNotTransferred=True,productTestsExecuted=0))
    print(json.dumps(dict(actualExit=0,pmd=3,manifestSha256=host.sha(out/'manifest.json'))))
