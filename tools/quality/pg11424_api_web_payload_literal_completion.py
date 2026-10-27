"""Bind original52 API/Web payload fixed-oracle tests, exact source and two covered Main classes and incomplete whole coverage."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11424-api-web-payload-literal-completion-v1'
SOURCE = '2d733dbd80350c819b732ae3d9b9b0f85ba0172f'
PINS = {
    'normal':('PG11412-api-web-payload-literal-six-compile-v1','b560ea0179e27b26375d96e7deb6f39deba5e728a2c5d57ed0fee6c46a67933d'),
    'recoveredOriginalPt':('PG11414-api-web-payload-literal-host-v1','f47bf80442534ebe48654d2f63326f88a18d37e94bb14b8e3ba129962fd7d3d7'),
    'post':('PG11418-api-web-payload-literal-post-v1','74c379b605d5f9ae303a573c164b13bb9351296aced3d64494d7a049c788bd44'),
    'trace':('PG11420-api-web-payload-literal-trace-v1','e4685b78781aa5582fb38d4e4a9fa75d3a317abf3fbb8f04a036c1c270801618'),
    'contexts':('PG11419-api-web-payload-literal-context-v1','e964c90a01aabb69a408b5a233007e0789e5e4c07cfa8d4b214c15d5c0f4f55c'),
    'contextsPost':('PG11421-api-web-payload-literal-context-post-v1','a306fbe009e3ea469fd989820459052e9c5f2e314a05866a2ce44585a546fd45'),
    'tracePost':('PG11422-api-web-payload-literal-trace-post-v1','d8fb89f35eda47a34bc4721f3b5e97b13754ddb3f724af39f2903c15def038a2')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11416-api-web-payload-literal-static-v1/manifest.json'
    static_sha = '96de97e2bcc97858d0a79086c068965db3c1cbe7195f275a8889c142481048e5'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2201_API・Web payload同値fixture PGPT仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2202_API・Web payload同値fixture結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1912'],relatedYkt=['YKT-1661'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent SS standard-source owner/retry/identity/order and self-JVM public MXBean vectors; original assertions/deadlines retained; F/E/S/aborted0',
        actual=dict(tests=52,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        artifactMeasurements=measurement,completeArtifactsFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=24,
        sourceLocalContextsReviewed=24,unclassifiedRaw=0,residualApplicability='RAW24_THREAD22_IMMEDIATE_CLOSE2_CONTEXT_ONLY_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


