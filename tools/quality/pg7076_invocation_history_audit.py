"""Append-only provenance limitation index; never reconstruct past argv or rerun prior jobs."""
import datetime
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7076-invocation-history-audit-v1'
PINS={
 'PG7068-timed-filesystem-host-v2':'3a375183d403d80c1d5c12fb0201d03bb7486d3a5ba4bc617451510d36770223',
 'PG7070-timed-filesystem-post-v2':'55456e2cb24d49f35766b3a17179c56a0e133a484592235529eb4eb7f61ac25a'}


def require(value,message):
    if not value:raise ValueError(message)


def main():
    invocation=capture(Path(__file__))
    require(not OUT.exists(),'new-only append index, old manifests unchanged')
    rows=[]
    for path in sorted(host.BASE.glob('PG*/manifest.json')):
        match=re.fullmatch(r'PG(\d+)-.+',path.parent.name)
        if not match or not 6990<=int(match[1])<=7066:continue
        raw=json.loads(path.read_bytes())
        begin=raw.get('begin',{})
        observed=raw.get('invocation') or begin.get('invocation')
        command=raw.get('command')
        rows.append(dict(path=str(path.relative_to(host.ROOT)),sha256=host.sha(path),
          source=raw.get('source') or begin.get('source'),recordedCommandType=type(command).__name__,
          recordedCommandSha256=hashlib.sha256(json.dumps(command,sort_keys=True).encode()).hexdigest(),
          pythonEntrypointStatus='ORIGINAL_OBSERVED_RECORD_PRESENT' if observed else 'ORIGINAL_SYS_ARGV_NOT_CAPTURED_DO_NOT_RECONSTRUCT',
          missingFields=None if observed else ['actualPythonArgv','separateWrapperHash'],
          originalChildCommandsAndResultsNotChanged=True))
    require(len(rows)>=20,'bounded whole historical continuous-v2 witness set')
    repaired=[]
    for label,digest in PINS.items():
        path=host.BASE/label/'manifest.json';raw=json.loads(path.read_bytes())
        require(host.sha(path)==digest and raw['actualExit']==0,'genuine fixed-source originals')
        observed=raw.get('invocation') or raw.get('begin',{}).get('invocation')
        require(observed and observed['provenance']=='OBSERVED_SYS_ARGV_AND_ORIG_ARGV_NOT_RECONSTRUCTED',
                'new original actually captured Python invocation')
        verify(observed)
        repaired.append(dict(path=str(path.relative_to(host.ROOT)),sha256=digest,
          invocation=observed,originalObservedToolBytesStillExact=True))
    scripts=['host_tool_invocation_test.py','host_tool_invocation_rollout_test.py']
    result=subprocess.run(['python3','-B','-m','unittest',*[Path(p).stem for p in scripts],'-v'],
      cwd=host.ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
      env={**os.environ,'PYTHONPATH':str(host.ROOT/'tools/quality')})
    require(result.returncode==0 and 'Ran 7 tests' in result.stderr and result.stderr.rstrip().endswith('OK'),
            'exact seven owned-fixture management tests, no Production tests')
    value=dict(actualExit=0,head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip(),
      timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,
      historicalRows=rows,historicalOriginalsNotModified=True,pastArgvReconstructed=False,
      newOriginalInvocationProofs=repaired,managementTests=dict(actualExit=0,count=7,
        command=['python3','-B','-m','unittest',*[Path(p).stem for p in scripts],'-v'],
        stdout=result.stdout,stderr=result.stderr,testSources={p:host.sha(host.ROOT/'tools/quality'/p) for p in scripts}),
      bug='BUG-1648',rollout='YKT-1401',productionTestsExecuted=0,actualVmActions=0,
      oldSuccessTestsRepeated=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation)
    os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,historicalRecords=len(rows),managementTests=7,
                         newOriginalProofs=len(repaired),manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
