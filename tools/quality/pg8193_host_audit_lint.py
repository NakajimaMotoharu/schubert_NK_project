"""Independent source-only audit of exact unused-binding cleanup and actual lint exits; no PT replay."""
import datetime
import json
import os
from pathlib import Path
import subprocess
from host_tool_invocation import capture,verify
import pg6966_chr_adapter_host as host

OUT=host.BASE/'PG8193-host-audit-lint-v1'
SLOT=host.W/'pg8193-host-audit-lint-v1'
PAIRS=(
 ('4051d8eca57539ba008c9cff7904be81b34edb52','tools/quality/pg8184_web_prometheus_gauge_post.py',
  "    compiled=json.loads((contract.COMPILE/'manifest.safe.json').read_bytes())\n"),
 ('a2a5f16f3','tools/quality/pg8192_mq_prometheus_gauge_post.py','import hashlib\n'))
SCRIPTS=('tools/quality/pg8184_web_prometheus_gauge_post.py','tools/quality/scoped_prometheus_host.py',
         'tools/quality/pg8190_mq_prometheus_gauge_host.py','tools/quality/pg8192_mq_prometheus_gauge_post.py')


def main():
    invocation=capture(Path(__file__))
    if OUT.exists() or SLOT.exists():
        raise ValueError('new-only own source/lint proof')
    os.umask(0o077)
    SLOT.mkdir()
    cleanup=[]
    for commit,path,removed in PAIRS:
        full=subprocess.check_output(['git','rev-parse',commit],cwd=host.ROOT,text=True).strip()
        old=subprocess.check_output(['git','show',full+':'+path],cwd=host.ROOT).decode()
        current=(host.ROOT/path).read_text()
        if old.count(removed)!=1 or old.replace(removed,'',1)!=current:
            raise ValueError('only recorded unused binding removal; no test/oracle/measurement algorithm change')
        cleanup.append(dict(path=path,originalCommit=full,currentSha256=host.sha(host.ROOT/path),
                            transformation='SINGLE_UNUSED_BINDING_LINE_REMOVAL_ONLY'))
    env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',
             PYTHONPATH=str(host.TC/'pyflakes-3.4.0/runtime'))
    command=['/usr/bin/python3','-B','-m','pyflakes',*SCRIPTS]
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    host.write(SLOT/'begin.safe.json',dict(command=command,startUTC=start,environment=env))
    child=subprocess.Popen(command,cwd=host.ROOT,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    host.write(SLOT/'process.safe.json',dict(pid=child.pid,ownerPid=os.getpid(),command=command,cwd=str(host.ROOT)))
    out,err=child.communicate(timeout=30)
    terminal=dict(actualExit=child.returncode,stdoutBytes=len(out),stderrBytes=len(err),
                  endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
    host.write(SLOT/'exit.safe.json',terminal)
    if child.returncode!=0 or out or err:
        raise ValueError('lint nonzero/unknown must stop downstream; do not start any other job')
    verify(invocation)
    value=dict(actualExit=0,invocation=invocation,cleanup=cleanup,command=command,terminal=terminal,
        sourceHashes={p:host.sha(host.ROOT/p) for p in SCRIPTS},toolSourceOnly=True,
        startUTC=start,timeUTC=terminal['endUTC'],productTestsExecuted=0,staticTargetAnalysisReplayed=False,
        actualVmActions=0,actualNetworkActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False)
    OUT.mkdir()
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,scripts=len(SCRIPTS),exactBindingOnlyChanges=len(cleanup),
                         manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
