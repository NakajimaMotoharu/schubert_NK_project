"""Bounded current public source hook audit, no application/process/network execution."""
import datetime
import json
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture, verify

SOURCE = 'e81adb96849e4067beb12f212350ab4fbd4b1998'
OUT = host.BASE / 'PG8628-c07-current-hook-audit-v1'

if __name__ == '__main__':
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT) == b''
    roots = [f'src/schubert-nk-{role}/src/main/java' for role in ('api','web','batch')]
    tokens = ['ApiStandardMetrics','WebStandardMetrics','BatchStandardMetrics','ApiMetricScrape','WebMetricScrape','BatchMetricText','HttpMetricValve','DbQueryDurationMetricCollector']
    command = ['rg','-n','--glob','*.java','--glob','!**/monitoring/**',*sum((['-e', token] for token in tokens),[]),*roots]
    search = subprocess.run(command,cwd=host.ROOT,capture_output=True,text=True,check=False)
    assert search.returncode in (0,1)
    assert search.stdout == '' and search.returncode == 1
    files = [f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/bootstrap/{title}ManagementServer.java' for role,title in (('api','Api'),('web','Web'))]
    files += [f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring/{title}StandardMetrics.java' for role,title in (('api','Api'),('web','Web'),('batch','Batch'))]
    records = []
    for path in files:
        content = subprocess.check_output(['git','show',SOURCE+':'+path],cwd=host.ROOT)
        import hashlib
        assert hashlib.sha256(content).hexdigest() == host.sha(host.ROOT/path)
        records.append(dict(path=path,sha256=host.sha(host.ROOT/path)))
    for path,role in zip(files[:2],('api','web')):
        text = (host.ROOT/path).read_text()
        assert '"/actuator/prometheus"' in text and 'schubert_nk_'+role+'_ready' in text
        assert not any(token in text for token in tokens)
    verify(invocation)
    OUT.mkdir()
    value = dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,sourceFiles=records,search=dict(command=command,actualExit=search.returncode,output=search.stdout,semantics='NO_OUTSIDE_MONITORING_REFERENCE_FOR_EXACT_DECLARED_TOKENS_NOT_A_RUNTIME_PROOF'),currentManagementMetrics='LEGACY_READY_GAUGE_ONLY',nextPermittedPg='ROLE_LOCAL_PURE_READY_PLUS_APPROVED_CUSTOM_TEXT; NO_EXISTING_ENDPOINT_EDIT_OR_HTTP_OPERATION',unaccepted=['production standard source and formatter wiring','standard SDK text exporter','HTTP terminal valve wiring','DB duration clock/query hook','MQ terminal hook','actual workload and management endpoint verification'],productTestsExecuted=0,newProductionClasses=0,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,whole451Accepted=False)
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,outsideReferences=0,managementReadinessOnly=2,productTestsExecuted=0,manifestSha256=host.sha(OUT/'manifest.json'))))
