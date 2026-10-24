"""Preserve source/normal failure imports before correction; all32 remain unrun."""
import json
from pathlib import Path
import re
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

if __name__=='__main__':
    invocation=capture(Path(__file__))
    run=host.W/'pg8702-web-batch-standard-source-six-compile-v1'
    out=host.BASE/'PG8703-web-batch-fixture-import-stop-v1'
    assert not out.exists() and host.sha(run/'manifest.safe.json')=='8cf9e932daf17aeef4786fa03d0c248413a2adb514aef44060b73b8e93ced7ac'
    raw=json.loads((run/'manifest.safe.json').read_text())
    assert raw['actualExit']==1 and raw['testsExecuted']==0 and len(raw['jars'])==4
    rows=[]
    for role,title in (('web','Web'),('batch','Batch')):
        for scope,suffix in (('main',''),('test','Test')):
            path=f'src/schubert-nk-{role}/src/{scope}/java/dev/codex/schubert/nk/{role}/monitoring/{title}StandardMetricSource{suffix}.java'
            assert host.sha(host.ROOT/path)==host.sha(run/'snapshot'/path)==raw['begin']['inputHashes'][path]
            imports=re.findall(r'^import (?:static )?([^;]+);$',(host.ROOT/path).read_text(),re.M)
            rows.append(dict(path=path,sha256=host.sha(host.ROOT/path),imports=imports))
    errors=[line for line in (run/'maven.log').read_text().splitlines() if '[ERROR]' in line][:12]
    verify(invocation)
    out.mkdir()
    host.write(out/'manifest.json',dict(bug='BUG-1714',ykt='YKT-1465',source=raw['source'],invocation=invocation,normalManifestSha256=host.sha(run/'manifest.safe.json'),actualExit=1,jarsCompleted=4,productTestsExecuted=0,planned32='UNRUN',sourceRows=rows,originalLogSha256=host.sha(run/'maven.log'),boundedErrors=errors,mainChangeRequired=False,expectedOrCountsChangeRequired=False))
    print(json.dumps(dict(actualExit=0,manifestSha256=host.sha(out/'manifest.json'))))
