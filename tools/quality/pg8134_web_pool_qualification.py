"""Exact Web77 source/run/environment qualification only; no whole451, real DB or native acceptance."""
import datetime
import json
import platform
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg8122_web_pool_six_compile as compilation
from host_tool_invocation import capture,verify
OUT=host.BASE/'PG8134-web-pool-qualification-v1'
NAMES=('PG8122-web-pool-six-compile-v1','PG8124-web-pool-host-v1','PG8126-web-pool-post-v1',
 'PG8128-web-pool-six-post-v1','PG8130-web-pool-trace-v1','PG8132-web-pool-review-v1')
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
      and run['begin']['expectedTests']==114 and len(run['cases'])==114 and all(r['result']=='PASS' for r in run['cases'])
      and c['tests']==114 and c['suites']==14 and len(c['sourceFiles'])==29 and len(c['executableClasses'])==25
      and c['actualCrcMismatch']==0 and c['actualSessions']==1 and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values())
      and physical['allPhysicalClassCount']==1799 and physical['oldPhysicalUnchanged']==1669
      and len(trace['sourceRows'])==147 and len(trace['physicalRows'])==130
      and review['generatedMethodCount']==36 and review['rawPmdFindings']==16 and review['unclassified']==review['actualViolationsOutstanding']==0
      and review['staticMissingClasses']==0 and len(review['metadataNegativeGuards'])==7
      and len(review['domainNegativeGuards'])==8 and len(c['metadataClasses'])==2 and len(c['additionalTypedPoolLibraryJarHashes'])==2
      and review['additionalTypedPoolLibraryJarHashes']==c['additionalTypedPoolLibraryJarHashes']):raise ValueError('all declared limited source/run quality conditions')
    spec=host.ROOT/'evidence/01_PT/018_NK-OPS-001/1728_WebPool観測結線_単体テスト仕様書.md';osfile=Path('/etc/os-release')
    value=dict(actualExit=0,source=compilation.SOURCE,branchObservation='CURRENT_QUALIFICATION_TIME_NOT_INFERRED_START_BRANCH',invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      branch=subprocess.check_output(['git','branch','--show-current'],cwd=host.ROOT,text=True).strip(),startUTC=run['begin']['startUTC'],witnesses=witnesses,
      environment=dict(osReleaseSha256=host.sha(osfile),osRelease=osfile.read_text().splitlines()[:6],kernel=platform.release(),
        java=subprocess.check_output([str(host.TC/'jdk-25.0.4/bin/java'),'--version'],text=True).splitlines(),
        maven='3.9.12, exact normal command/source/dependencies in original begin',micrometer='1.17.1',jacoco='0.8.15',hikari='7.1.0 borrowed interfaces only',slf4j='2.0.18 fixed normal binding'),
      specification=dict(path=str(spec.relative_to(host.ROOT)),sha256=host.sha(spec),
        testIds=['WEBPOOLMET001..008','WEBPOOLREAD001..008','WEBPOOLCONN001..008']),
      tests=114,suites=14,newTestIds=24,necessaryExistingCasesRequalified=90,failed=0,errors=0,skipped=0,flaky=0,
      additionalTypedPoolLibraryJarHashes=c['additionalTypedPoolLibraryJarHashes'],typedPoolInterfaceClassSha256=review['typedPoolInterfaceClassSha256'],
      counters=c['counters'],actualCrcMismatch=0,actualSessions=1,staticRawPmdFindings=16,staticUnclassified=0,staticApplicableOutstanding=0,
      newStaticContextRationaleRows=3,spotbugsFindings=0,checkstyleFindings=0,bugs=[],horizontal=[],
      programScope='WEB_MONITORING_OWNED_SDK_PROXY_ONLY_NOT_REAL_HTTP_DB_ROOT',businessSchemaAccess=False,
      actualDatabaseActions=0,actualVmActions=0,actualNetworkActions=0,actualClockObservationByProduction=False,
      realSchemaConnectionOwnerSourceAccepted=False,exporterAccepted=False,productTestsExecutedByAssembly=0,
      coverageUnion=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,ptAlternative=0,qa051Final='HELD')
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,source=compilation.SOURCE,tests=114,suites=14,newTestIds=24,counters=c['counters'],manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()


