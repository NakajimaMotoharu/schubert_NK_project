"""Save exact original two metadata guard results; no Production PT/coverage or repeated metadata goal."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7741-web-classpath-receipt-guards-v1'

if __name__=='__main__':
    invocation=capture(Path(__file__))
    if OUT.exists():raise ValueError('new-only guard receipt')
    inputs={p:host.sha(host.ROOT/p) for p in ('tools/quality/web_classpath_receipt_contract.py',
      'tools/quality/tests/test_web_classpath_receipt_contract.py','tools/quality/pg7740_web_classpath_metadata.py')}
    command=[sys.executable,'-B','-m','unittest','tools.quality.tests.test_web_classpath_receipt_contract','-v']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(command,cwd=host.ROOT,capture_output=True,text=True,check=False)
    if inputs!={p:host.sha(host.ROOT/p) for p in inputs}:raise ValueError('all guard inputs fixed')
    verify(invocation);os.umask(0o077);OUT.mkdir();log=OUT/'result.log';log.write_text(result.stdout+result.stderr)
    host.write(OUT/'manifest.json',dict(actualExit=result.returncode,startUTC=started,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      invocation=invocation,command=command,inputHashes=inputs,methods=2,negativeMutations=8,logSha256=host.sha(log),
      productionPtExecuted=0,javaExecuted=False,metadataGoalReplayed=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0))
    print(json.dumps(dict(actualExit=result.returncode,methods=2,negativeMutations=8,manifestSha256=host.sha(OUT/'manifest.json'))))
    if result.returncode:raise SystemExit(result.returncode)
