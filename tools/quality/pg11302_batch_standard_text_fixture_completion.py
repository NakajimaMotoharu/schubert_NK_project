"""Bind original107 Batch standard-to-text tests, exact source, six covered Main and incomplete whole coverage."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11302-batch-standard-text-fixture-completion-v1'
SOURCE = 'd431ad964355c4e5c602fcb94fe0182da6ae3a61'
PINS = {
    'normal':('PG11290-batch-standard-text-fixture-six-compile-v1','e5f2c258d8faa0b303f3d74edae30c3dfc03adc3e8964290ac022e5d140104d9'),
    'recoveredOriginalPt':('PG11292-batch-standard-text-fixture-host-v1','2be0ee292fa79f16f9f2c5e938a6fa461ffd3eca72136e23b5ccd243270a9ee7'),
    'post':('PG11296-batch-standard-text-fixture-post-v1','b65202a2dd54786993e6f777de86903aa6b9ed1012df174f4dccfe0929c99012'),
    'trace':('PG11298-batch-standard-text-fixture-trace-v1','e8470cea0a40c8410e9520551ddb86b423746e04af735f91d7d9c14dc7da05eb'),
    'contexts':('PG11297-batch-standard-text-fixture-context-v1','0bc9214c567afda1d18ad4441b016c7ec780f59ec7ef31f5d118d015cf8f4be4'),
    'contextsPost':('PG11299-batch-standard-text-fixture-context-post-v1','f86c7f68cc9d8f0fa2d8c2772d6772bcd521c7e1869a35d439156d66e8dd2c86'),
    'tracePost':('PG11300-batch-standard-text-fixture-trace-post-v1','0920c4e255636a46f3666a25969a26bff943a1ab65c33282795be05a47788ce4')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11294-batch-standard-text-fixture-static-v1/manifest.json'
    static_sha = '8ebe64d8773c98c27db1180a4187829280886700c487c6c96021bdec9807ab63'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2179_Batch標準SDK・text六Test同値fixture仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2180_Batch標準SDK・text六Test同値fixture結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1907'],relatedYkt=['YKT-1658'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent SS Batch text golden, fixed binder ports and self-JVM public MXBean/failure/null/owner vectors; F/E/S/aborted0',
        actual=dict(tests=107,suites=6,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        selectedValueMainUnits=measurement['selectedValueMain'],completeBatchCounters=post['bundleCounters'],completeBatchFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=52,
        sourceLocalContextsReviewed=20,unclassifiedRaw=32,residualApplicability='RAW52_THREAD19_NULL1_CONTEXT_ONLY_CLOSE31_COMPARABLE1_UNCLASSIFIED_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


