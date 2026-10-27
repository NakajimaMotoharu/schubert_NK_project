"""Bind original42 plus six independent GC Fake tests, exact source, retained raw44 and incomplete whole coverage."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11456-gc-fake-guard-completion-v1'
SOURCE = '495313cd8e724d5f1906fca64d9d9fd3516aae50'
PINS = {
    'normal':('PG11444-gc-fake-guard-six-compile-v1','0f5f38eb4fc41cde15284301f8b57b53c4f22743004411b71ece13a60ed1edfb'),
    'recoveredOriginalPt':('PG11446-gc-fake-guard-host-v1','c849836c6b0356430eaaf4426718bc8307bc1d8cd5581eb659cd776e8a529e74'),
    'post':('PG11450-gc-fake-guard-post-v2','2e62cc35fc6c916cce3a6cce92d5e6bcc63ba1fc0779dca4fdfc69b6864342d7'),
    'trace':('PG11452-gc-fake-guard-trace-v1','6948323785d9859c81bee7e449fb538158bb95c91f5715571205a79ef2eada42'),
    'contexts':('PG11451-gc-fake-guard-context-v3','6c9486363b2b4c101036c92542be9fe945bb357aae447fbf5520370bb76f0cfb'),
    'contextsPost':('PG11453-gc-fake-guard-context-post-v3','ab7430e60bc819fbe2d938d077999ad886e274ee449787e28e73441d3b88d0e7'),
    'tracePost':('PG11454-gc-fake-guard-trace-post-v1','70c29cb6a5809e344409533071f398435b3100528d75d2594cb7eb7dec4d4711')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11448-gc-fake-guard-static-v1/manifest.json'
    static_sha = '4540e528ae063a80dfcdfa454da340a397e0449f006ee7692e95d19e8d86e185'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2207_三role GC Fake例外保全PGPT仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2208_三role GC Fake例外保全結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1913','BUG-1914','BUG-1915','BUG-1916'],relatedYkt=['YKT-1662','YKT-1663','YKT-1664','YKT-1665'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent SS standard-source owner/retry/identity/order and self-JVM public MXBean vectors; original assertions/deadlines retained; F/E/S/aborted0',
        actual=dict(tests=48,suites=3,newProductTestIds=6,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        artifactMeasurements=measurement,completeArtifactsFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=44,oldRawDiagnostics=38,newRawDiagnostics=6,
        sourceLocalContextsReviewed=36,unclassifiedRaw=8,residualApplicability='RAW44_THREAD6_DUPLICATE8_RETAINED_GC3_IMMEDIATE_CLOSE3_CONDITIONAL_FAKE18_NEW_FAKE6_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


