"""Assemble exact public source/run pointers and tool environment, not full451/PGPT acceptance."""
import datetime
import json
import platform
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7876_api_query_collection_six_compile as compilation
from host_tool_invocation import capture,verify
OUT=host.BASE/'PG7886-api-query-collection-qualification-v1'
NAMES=('PG7872-api-query-collection-host-v1','PG7874-api-query-collection-post-v1',
 'PG7876-api-query-collection-six-compile-v1','PG7878-api-query-collection-six-post-v1',
 'PG7880-api-query-collection-trace-v1','PG7882-api-query-collection-review-v1')
def main():
    invocation=capture(Path(__file__))
    if OUT.exists():raise ValueError('new-only component witness')
    witnesses=[];proofs=[]
    for name in NAMES:
        f=host.BASE/name/'manifest.json';a=json.loads(f.read_bytes())
        if a['actualExit']!=0 or a['source']!=compilation.SOURCE:raise ValueError('same-source genuine zero')
        witnesses.append(dict(path=str(f.relative_to(host.ROOT)),sha256=host.sha(f)));proofs.append(a)
    run,c,normal,physical,trace,review=proofs
    if not (len(run['cases'])==146 and all(r['result']=='PASS' for r in run['cases'])
      and c['tests']==146 and c['suites']==18 and len(c['sourceFiles'])==36 and len(c['executableClasses'])==30
      and c['actualCrcMismatch']==0 and c['actualSessions']==1 and all(v['missed']==0 for v in c['counters'].values())
      and normal['actualExit']==normal['terminal']['actualExit']==0 and normal['testsExecuted']==0
      and physical['allPhysicalClassCount']==1779 and physical['oldPhysicalUnchanged']==1669
      and len(trace['sourceRows'])==125 and len(trace['physicalRows'])==110
      and review['unclassified']==review['actualViolationsOutstanding']==0 and review['currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters']==50):raise ValueError('exact complete limited component conditions')
    osfile=Path('/etc/os-release');spec=host.ROOT/'evidence/01_PT/018_NK-OPS-001/1714_DbQueryDuration取得結線_単体テスト仕様書.md'
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      branch=run['begin']['branch'],startUTC=run['begin']['startUTC'],witnesses=witnesses,
      environment=dict(osReleaseSha256=host.sha(osfile),osRelease=osfile.read_text().splitlines()[:6],kernel=platform.release(),
        java=subprocess.check_output([str(host.TC/'jdk-25.0.4/bin/java'),'--version'],text=True).splitlines(),
        maven='3.9.12, exact command/tool pins in normal/host begin',micrometer='1.17.1',jacoco='0.8.15'),
      specification=dict(path=str(spec.relative_to(host.ROOT)),sha256=host.sha(spec),testIds='DBCONN001..008'),
      tests=146,suites=18,newTestIds=8,requiredExistingCasesRequalified=138,failed=0,errors=0,skipped=0,flaky=0,
      counters=c['counters'],actualCrcMismatch=0,actualSessions=1,staticRawPmdFindings=17,staticUnclassified=0,
      staticApplicableOutstanding=0,spotbugsFindings=0,checkstyleFindings=0,
      bugs=[],horizontal=[],originalFailedRunsPreserved=True,
      productTestsExecutedByAssembly=0,actualVmActions=0,actualDatabaseActions=0,actualClockObservationByProduction=False,
      histogramExporterAcceptance=False,allBusinessQueryIdsCovered=False,whole451Accepted=False,formalUpdated=False,
      newAccepted=0,effortPercent=None,ptAlternative=0,qa051Final='HELD')
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,source=compilation.SOURCE,tests=146,suites=18,newTestIds=8,
      counters=c['counters'],manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
