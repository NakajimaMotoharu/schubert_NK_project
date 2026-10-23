"""Save original exact terminal for new metadata guards, not Production PT/coverage."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7626-api-inbox-dependency-guards-v1'
INPUTS=('tools/quality/inbox_protocol_harness_contract.py',
 'tools/quality/tests/test_inbox_protocol_harness_contract.py',
 'tools/quality/pg7008_monitoring_mode_post.py',
 'tools/quality/tests/test_monitoring_dependency_partition.py',
 'tools/quality/harnesses/monitoring-api-jobs-pom.xml')

if __name__=='__main__':
    invocation=capture(Path(__file__))
    if OUT.exists():raise ValueError('new-only metadata guard receipt')
    hashes={p:host.sha(host.ROOT/p) for p in INPUTS}
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    command=[sys.executable,'-B','-m','unittest',
      'tools.quality.tests.test_inbox_protocol_harness_contract',
      'tools.quality.tests.test_monitoring_dependency_partition','-v']
    result=subprocess.run(command,cwd=host.ROOT,capture_output=True,text=True,check=False)
    if hashes!={p:host.sha(host.ROOT/p) for p in INPUTS}:raise ValueError('fixed guard inputs')
    verify(invocation);os.umask(0o077);OUT.mkdir()
    log=OUT/'result.log';log.write_text(result.stdout+result.stderr)
    value=dict(actualExit=result.returncode,startUTC=started,
      endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=command,
      invocation=invocation,inputHashes=hashes,logSha256=host.sha(log),
      methods=6,harnessNegativeMutations=8,dependencyPartitionMethods=4,
      earlierUnpersistedRunNotCounted=True,productionPtExecuted=0,javaExecuted=False,
      coverageUpdated=False,formalUpdated=False,newAccepted=0,effortPercent=None,
      actualVmActions=0,actualDatabaseActions=0)
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=result.returncode,methods=6,manifestSha256=host.sha(OUT/'manifest.json'))))
    if result.returncode:raise SystemExit(result.returncode)
