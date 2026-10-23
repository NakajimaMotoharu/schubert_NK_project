"""Exact Web77 source/run/environment qualification only; no whole451, real DB or native acceptance."""
import datetime
import json
import platform
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg8098_http_duration_nullable_six_compile as compilation
from host_tool_invocation import capture,verify
OUT=host.BASE/'PG8110-http-duration-nullable-qualification-v1'
NAMES=('PG8098-http-duration-nullable-six-compile-v1','PG8100-http-duration-nullable-host-v1','PG8102-http-duration-nullable-post-v1',
 'PG8104-http-duration-nullable-six-post-v1','PG8106-http-duration-nullable-trace-v1','PG8108-http-duration-nullable-review-v1')
def main():
    invocation=capture(Path(__file__))
    if OUT.exists():raise ValueError('new-only limited qualification')
    proofs=[];witnesses=[]
    for name in NAMES:
        f=host.BASE/name/'manifest.json';a=json.loads(f.read_bytes())
        if a['source']!=compilation.SOURCE or a['actualExit']!=0:raise ValueError('same source and genuine zero required')
        proofs.append(a);witnesses.append(dict(path=str(f.relative_to(host.ROOT)),sha256=host.sha(f)))
    normal,run,c,physical,trace,review=proofs
    if not (normal['terminal']['actualExit']==0 and normal['testsExecuted']==0 and normal['begin']['captureTestClasspath'] is True
      and run['begin']['expectedTests']==90 and len(run['cases'])==90 and all(r['result']=='PASS' for r in run['cases'])
      and c['tests']==90 and c['suites']==11 and len(c['sourceFiles'])==23 and len(c['executableClasses'])==20
      and c['actualCrcMismatch']==0 and c['actualSessions']==1 and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values())
      and physical['allPhysicalClassCount']==1794 and physical['oldPhysicalUnchanged']==1669
      and len(trace['sourceRows'])==141 and len(trace['physicalRows'])==125
      and review['generatedMethodCount']==27 and review['rawPmdFindings']==13 and review['unclassified']==review['actualViolationsOutstanding']==0
      and review['staticMissingClasses']==0 and len(review['metadataNegativeGuards'])==7
      and len(review['domainNegativeGuards'])==7 and len(c['metadataClasses'])==2):raise ValueError('all declared limited source/run quality conditions')
    spec=host.ROOT/'evidence/01_PT/018_NK-OPS-001/1725_HTTP極小MAX累積_追加品質単体テスト仕様書.md';osfile=Path('/etc/os-release')
    value=dict(actualExit=0,source=compilation.SOURCE,branchObservation='CURRENT_QUALIFICATION_TIME_NOT_INFERRED_START_BRANCH',invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      branch=subprocess.check_output(['git','branch','--show-current'],cwd=host.ROOT,text=True).strip(),startUTC=run['begin']['startUTC'],witnesses=witnesses,
      environment=dict(osReleaseSha256=host.sha(osfile),osRelease=osfile.read_text().splitlines()[:6],kernel=platform.release(),
        java=subprocess.check_output([str(host.TC/'jdk-25.0.4/bin/java'),'--version'],text=True).splitlines(),
        maven='3.9.12, exact normal command/source/dependencies in original begin',micrometer='1.17.1',jacoco='0.8.15'),
      specification=dict(path=str(spec.relative_to(host.ROOT)),sha256=host.sha(spec),
        testIds=['HTTPREC010','HTTPDUR001..012']),
      tests=90,suites=11,newTestIds=13,necessaryExistingCasesRequalified=77,failed=0,errors=0,skipped=0,flaky=0,
      counters=c['counters'],actualCrcMismatch=0,actualSessions=1,staticRawPmdFindings=13,staticUnclassified=0,staticApplicableOutstanding=0,
      newStaticContextRationaleRows=0,spotbugsFindings=0,checkstyleFindings=0,bugs=['BUG-1681','BUG-1682','BUG-1683','BUG-1684','BUG-1685'],horizontal=['YKT-1432','YKT-1433','YKT-1434','YKT-1435','YKT-1436'],
      programScope='WEB_MONITORING_OWNED_SDK_PROXY_ONLY_NOT_REAL_HTTP_DB_ROOT',businessSchemaAccess=False,
      actualDatabaseActions=0,actualVmActions=0,actualNetworkActions=0,actualClockObservationByProduction=False,
      realSchemaConnectionOwnerSourceAccepted=False,exporterAccepted=False,productTestsExecutedByAssembly=0,
      coverageUnion=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,ptAlternative=0,qa051Final='HELD')
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,source=compilation.SOURCE,tests=90,suites=11,newTestIds=13,counters=c['counters'],manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()

