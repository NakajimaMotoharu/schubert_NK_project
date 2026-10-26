"""Join fixed source, original request case results and complete API misses; no execution."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11092-inbox-lifecycle-completion-v1'
SOURCE = 'f97723798f3f71a9112b4bbecfba531dba9b34b6'
PINS = {
    'normal':('PG11080-inbox-lifecycle-six-compile-v1','a58e4f704b97a8fc58ff094db32231e455767e5b15972af3b66fc933f91a3641'),
    'recoveredOriginalPt':('PG11082-inbox-lifecycle-host-v1','1c782ecf14445873af983fb36302b89babc9197049b87c3307781843f35ea0b3'),
    'post':('PG11086-inbox-lifecycle-post-v1','09269e164031c8533a7517eb1b3e6fccd91cc0adfce00e824bd291656bb6c200'),
    'trace':('PG11088-inbox-lifecycle-trace-v1','101373b2083eef99ffa38c42f9182c2475546846efeaa515e30ea40e343ec5fd'),
    'tracePost':('PG11090-inbox-lifecycle-trace-post-v1','3c23032788d499d213d6a7a1e977673d95fac6a59bfd868b5f441d58d7e0f3a2')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11084-inbox-lifecycle-static-v1/manifest.json'
    static_sha = 'd7aaaad5997bd39faeb386dcdfbc5c605c8f42cdf5c51f6eea9fe7423d6a8404'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 0 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2145_Inbox純粋値四Test同値fixture PGPT仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2146_Inbox純粋値四Test・所有是正結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-MSG-002','NK-QRY-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1894','BUG-1895','BUG-1896'],relatedYkt=['YKT-1645','YKT-1646','YKT-1647'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent OpenSSL/SS324 LP/JCE/fixed byte/null/expiry/SQLSTATE/scope vectors and cleanup assertions; F/E/S/aborted0',
        actual=dict(tests=15,suites=4,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        selectedValueMainUnits=measurement['selectedValueMain'],completeApiCounters=post['bundleCounters'],completeApiFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=0,rawPmd=0,
        residualApplicability='NONE_IN_SELECTED_FOUR_TEST_SOURCES',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()

