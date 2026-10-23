"""BUG1664: first frozen fake-writer integration, no real events/production PT/quota operation."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

SLOT=host.W/'pg7517-quota-binding-writer-post-v1'
OUT=host.BASE/'PG7517-quota-binding-writer-post-v1'
FILES=['tools/quality/pmo_quota_binding.py','tools/quality/tests/test_pmo_quota_binding.py',
 'tools/quality/tests/test_pmo_quota_binding_writer.py','tools/quality/pg7517_quota_binding_writer_post.py']

def main():
    invocation=capture(Path(__file__))
    if SLOT.exists() or OUT.exists():raise ValueError('new-only original writer check, never repeat unknown job')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip()
    for file in FILES:
        raw=subprocess.check_output(['git','show',source+':'+file],cwd=host.ROOT)
        if hashlib.sha256(raw).hexdigest()!=host.sha(host.ROOT/file):raise ValueError('frozen tool source required')
    hashes={p:host.sha(host.ROOT/p) for p in FILES};events=host.ROOT.parent/'PMO/pgpt-execution-metrics/events.jsonl'
    # Event append-only tail may change via legitimate PMO; our integration patches the writer
    # and tests only own temporary metadata. It never calls get_usage_limits or a real append.
    command=['python3','-B','-Werror','-m','unittest','discover','-s','tools/quality/tests','-p','test_pmo_quota_binding_writer.py','-v']
    os.umask(0o077);SLOT.mkdir();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    done=subprocess.run(command,cwd=host.ROOT,capture_output=True,text=True)
    host.write(SLOT/'exit.safe.json',dict(command=command,startUTC=started,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actualExit=done.returncode))
    (SLOT/'stdout.safe.log').write_text(done.stdout);(SLOT/'stderr.safe.log').write_text(done.stderr)
    if done.returncode or 'Ran 4 tests' not in done.stderr or not done.stderr.rstrip().endswith('OK'):
        raise ValueError('all four actual writer integration checks required')
    if any(host.sha(host.ROOT/p)!=h for p,h in hashes.items()):raise ValueError('tool inputs changed during run')
    value=dict(actualExit=0,source=source,invocation=invocation,files=hashes,command=command,startUTC=started,
      endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),toolTests=4,failures=0,errors=0,skipped=0,
      stdoutSha256=host.sha(SLOT/'stdout.safe.log'),stderrSha256=host.sha(SLOT/'stderr.safe.log'),
      pure10OriginalResult=dict(toolChunk='3088b5',actualExit=0,tests=10,failures=0,errors=0,skipped=0,
        executionTimeUTC=None,timeNotInvented=True,sourceHashesCapturedAfterFirstRun=True,notReplayed=True),
      currentRealEventsPath=str(events),realEventsAppendedByTest=0,actualQuotaApiCalls=0,
      actualVmActions=0,actualDatabaseActions=0,productionTests=0,sourceInputsUnchanged=True,
      relatedBug='BUG-1664',relatedExpansion='YKT-1415',formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,writerToolTests=4,pureOriginal10NotReplayed=True,productionTests=0,
      manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
