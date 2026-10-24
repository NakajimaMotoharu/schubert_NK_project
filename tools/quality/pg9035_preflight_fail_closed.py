"""BUG1729 benign lint canaries only; production/static jobs and legacy caller tool never rerun."""
import datetime as dt
import json
from pathlib import Path
import shlex
import subprocess
import sys
from host_tool_invocation import capture,verify
from public_blob_scan import sha

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9035-preflight-fail-closed-v1'
PYFLAKES=ROOT.parent/'toolchain/pyflakes-3.4.0/runtime'


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    old=ROOT/'tools/quality/pg9033_api_service_caller_context.py'
    new=ROOT/'tools/quality/pg9033_api_service_caller_context_v2.py'
    assert sha(old.read_bytes())=='9c1492632fd3c2c573e7e42424f156ff524af0ff20162d57c6477a9fb98fb6fc'
    assert new.read_text()==old.read_text().replace('import re\n','',1).replace('PG9033-api-service-caller-context-v1','PG9033-api-service-caller-context-v2')
    env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','PYTHONNOUSERSITE':'1','PYTHONPATH':str(PYFLAKES)}
    rows=[]
    for name,file,failfast,expected in [('pass','preflight-pass.py.txt',True,0),
          ('lint-stop-before-child73','preflight-reject.py.txt',True,1),
          ('synthetic-broken-gate-control','preflight-reject.py.txt',False,73)]:
        path=ROOT/'tools/quality/tests/fixtures'/file
        text=('set -e\n' if failfast else '')+shlex.join([sys.executable,'-B','-m','pyflakes',str(path)])+'\n'+shlex.join([sys.executable,'-B',str(path)])
        start=dt.datetime.now(dt.timezone.utc).isoformat()
        result=subprocess.run(['/bin/bash','-c',text],cwd=ROOT,env=env,capture_output=True,timeout=15,check=False)
        assert result.returncode==expected and not result.stderr
        if expected in (1,73):assert b"'math' imported but unused" in result.stdout
        else:assert not result.stdout
        rows.append(dict(name=name,command=['/bin/bash','-c',text],startUTC=start,
             endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),actualExit=result.returncode,
             expectedControlExit=expected,inputSha256=sha(path.read_bytes()),
             outcome='EXPECTED_LINT_STOP_CHILD_NOT_REACHED' if failfast and expected==1 else 'EXPECTED_SYNTHETIC_CONTROL',
             realJobsOrTargetsInvoked=False))
    for name,path,expected in [('original-unused-re-reproduced',old,1),('corrected-import-lint',new,0)]:
        command=[sys.executable,'-B','-m','pyflakes',str(path)]
        result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,timeout=15,check=False)
        assert result.returncode==expected and not result.stderr
        if expected:assert b"'re' imported but unused" in result.stdout
        else:assert not result.stdout
        rows.append(dict(name=name,command=command,actualExit=result.returncode,expectedControlExit=expected,
                         inputSha256=sha(path.read_bytes()),legacyToolExecuted=False))
    current=BASE/'PG9033-api-service-caller-context-v2/manifest.json'
    fixed=json.loads(current.read_bytes());assert fixed['actualExit']==0
    assert fixed['applicabilityUnclassified']==fixed['productTestsExecuted']==0
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          source='73d94fc525c6ea8828ca82d906ec583146fee7bf',bug='BUG-1729',ykt='YKT-1480',
          controls=rows,syntheticFailFastCases=3,actualLintReproductions=2,
          oldVersionQualified=False,newVersionLintQualified=True,oldVersionPreserved=True,
          newContextManifestSha256=sha(current.read_bytes()),productJobsRerun=0,
          actualTargetServiceOrVmActions=0,productTestsExecuted=0,formalUpdated=False,newAccepted=0)
    with (OUT/'manifest.json').open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,syntheticFailFastCases=3,actualLintReproductions=2,productJobsRerun=0)))


if __name__=='__main__':main()
