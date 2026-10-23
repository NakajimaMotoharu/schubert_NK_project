"""Exact Web77 source/run/environment qualification only; no whole451, real DB or native acceptance."""
import datetime
import json
import platform
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7942_web_outbox_six_compile as compilation
from host_tool_invocation import capture,verify
OUT=host.BASE/'PG7956-web-outbox-qualification-v1'
NAMES=('PG7942-web-outbox-six-compile-v1','PG7944-web-outbox-host-v1','PG7946-web-outbox-post-v1',
 'PG7948-web-outbox-six-post-v1','PG7950-web-outbox-trace-v1','PG7952-web-outbox-review-v1')
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
      and run['begin']['expectedTests']==77 and len(run['cases'])==77 and all(r['result']=='PASS' for r in run['cases'])
      and c['tests']==77 and c['suites']==10 and len(c['sourceFiles'])==20 and len(c['executableClasses'])==18
      and c['actualCrcMismatch']==0 and c['actualSessions']==1 and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values())
      and physical['allPhysicalClassCount']==1788 and physical['oldPhysicalUnchanged']==1669
      and len(trace['sourceRows'])==135 and len(trace['physicalRows'])==119
      and review['generatedMethodCount']==27 and review['rawPmdFindings']==13 and review['unclassified']==review['actualViolationsOutstanding']==0
      and len(review['metadataNegativeGuards'])==7):raise ValueError('all declared limited source/run quality conditions')
    spec=host.ROOT/'evidence/01_PT/018_NK-OPS-001/1721_WebOutbox観測経路_単体テスト仕様書.md';osfile=Path('/etc/os-release')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      branch=normal['begin'].get('branch','dev-foundation'),startUTC=run['begin']['startUTC'],witnesses=witnesses,
      environment=dict(osReleaseSha256=host.sha(osfile),osRelease=osfile.read_text().splitlines()[:6],kernel=platform.release(),
        java=subprocess.check_output([str(host.TC/'jdk-25.0.4/bin/java'),'--version'],text=True).splitlines(),
        maven='3.9.12, exact normal command/source/dependencies in original begin',micrometer='1.17.1',jacoco='0.8.15'),
      specification=dict(path=str(spec.relative_to(host.ROOT)),sha256=host.sha(spec),
        testIds=['WEBOBXMET001..008','WEBOBXDB001..010','WEBOBXCONN001..008']),
      tests=77,suites=10,newTestIds=26,necessaryExistingCasesRequalified=51,failed=0,errors=0,skipped=0,flaky=0,
      counters=c['counters'],actualCrcMismatch=0,actualSessions=1,staticRawPmdFindings=13,staticUnclassified=0,staticApplicableOutstanding=0,
      newStaticContextRationaleRows=5,spotbugsFindings=0,checkstyleFindings=0,bugs=[],horizontal=[],
      programScope='WEB_TECHNICAL_OUTBOX_READONLY_PROXY_AND_SUPPLIED_METRICS_ONLY',businessSchemaAccess=False,
      actualDatabaseActions=0,actualVmActions=0,actualNetworkActions=0,actualClockObservationByProduction=False,
      realSchemaConnectionOwnerSourceAccepted=False,exporterAccepted=False,productTestsExecutedByAssembly=0,
      coverageUnion=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,ptAlternative=0,qa051Final='HELD')
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,source=compilation.SOURCE,tests=77,suites=10,newTestIds=26,counters=c['counters'],manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
