"""Bind original44 memory HTTP fixed-oracle tests, exact source and two covered Main classes and incomplete whole coverage."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11516-metric-http-literal-completion-v1'
SOURCE = '60d702bf8d83b6c4c8531397a7b770234fd9cf6e'
PINS = {'normal': ('PG11504-metric-http-literal-six-compile-v1', '8a626280621377d27599da1616906f6f1ef2d6f83420e25d495554392b250b11'), 'recoveredOriginalPt': ('PG11506-metric-http-literal-host-v1', 'fb5845c64102ca6f4d1cb51663180f1f4a91a82f3cf641ea5e0afd31b10d16bb'), 'post': ('PG11510-metric-http-literal-post-v1', '9b9b3f211101bc75ec7110dc445335108ebd2dd742c6157818733fe2556b49c3'), 'trace': ('PG11512-metric-http-literal-trace-v1', 'f1cae2504e3d9b6e16840e344d8fefcbf06439386e511c1f9a3f95f2c60b8846'), 'tracePost': ('PG11514-metric-http-literal-trace-post-v1', '6c1ca4140790ef7ad99ab67617024dac4f033658a822db70d43ad9ba2584f42e')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11508-metric-http-literal-static-v1/manifest.json'
    static_sha = 'fa8d830558c7799fd70f71104ed49c9cc559e31d3677e73b4a16b12f6072b678'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2215_API・WebメモリMetric HTTP同値fixture仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2216_API・WebメモリMetric HTTP同値fixture結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1920'],relatedYkt=['YKT-1669'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent fixed GET/raw-path/405404/ready text/header/status/UTF8 byte lengths/Throwable identity/borrowed-write close and typed getter vectors; F/E/S/aborted0',
        actual=dict(tests=44,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        artifactMeasurements=measurement,completeArtifactsFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=52,
        sourceLocalContextsReviewed=0,unclassifiedRaw=52,residualApplicability='RAW52_RESOURCE_APPLICABILITY_UNCLASSIFIED_RETAINED_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


