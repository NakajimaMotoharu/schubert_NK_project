"""Bind original10 HTTP recorder tests, exact source, six covered Main and incomplete whole coverage."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11276-http-recorder-fixture-completion-v1'
SOURCE = '064294de0f47e195a99e5fab76e2fe92ea31256d'
PINS = {
    'normal':('PG11264-http-recorder-fixture-six-compile-v1','87b29c22a2f3b612936173d8633cd67201368bc1f711938a0f1e834624f17d9f'),
    'recoveredOriginalPt':('PG11266-http-recorder-fixture-host-v1','41f388d0a8a32625df7f7027d14da8f818f5675e91a77d1f3d9412db9844df3c'),
    'post':('PG11270-http-recorder-fixture-post-v1','f7ceae2ed73908611087376aec80f948e074973079202bebe177f7bbe751365d'),
    'trace':('PG11272-http-recorder-fixture-trace-v1','aa24fa0f0e376c2719293f1ab8681973cfb100e429c2d8e4c1d0d8a39292eb4c'),
    'contexts':('PG11271-http-recorder-fixture-context-v1','3794a7f23d8a923c689dc7c7e50e299bca308559c9f9dd3682b68bac39e204db'),
    'contextsPost':('PG11273-http-recorder-fixture-context-post-v1','6056bcc746860f557acac91224ccd1b5953a127941d986993143658f28a53a9c'),
    'tracePost':('PG11274-http-recorder-fixture-trace-post-v1','5cf88859e12200e90ad2228f1abc1403896d37339797180ea6a16ed23ef521f0')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11268-http-recorder-fixture-static-v1/manifest.json'
    static_sha = 'def0cf0a74811d7de0e2c38f64f96932b0abb71fe44fef5388ee36ac88516c7a'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2175_HTTP metric recorder同値fixture・executor仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2176_HTTP metric recorder同値fixture・executor結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1906'],relatedYkt=['YKT-1657'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent SS HTTP route resource/label/bucket/extreme/failure/null/owner vectors; F/E/S/aborted0',
        actual=dict(tests=10,suites=1,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        selectedValueMainUnits=measurement['selectedValueMain'],completeWebCounters=post['bundleCounters'],completeWebFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=6,
        sourceLocalContextsReviewed=6,unclassifiedRaw=0,residualApplicability='RAW6_LOADER1_THREAD4_CALLER_ACTUAL_MAP1_RETAINED_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


