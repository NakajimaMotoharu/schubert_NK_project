"""Bind original30 supplied Batch metric/label tests, exact source, six covered Main and incomplete whole coverage."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11250-batch-supplied-metric-label-fixture-completion-v1'
SOURCE = 'ef86a244b2f528a2d60bd0f22a94a853ce3146ff'
PINS = {
    'normal':('PG11238-batch-supplied-metric-label-fixture-six-compile-v1','5c832221f384ea840e6a9b5cf9b55e7c6f797e472647d7831c3a8ad1409f0bbe'),
    'recoveredOriginalPt':('PG11240-batch-supplied-metric-label-fixture-host-v1','2e2c94c28133d04129e7a5a9e84e716dbf64f1acc7c2b524c9962b871fd4db0a'),
    'post':('PG11244-batch-supplied-metric-label-fixture-post-v1','bbe1078458fcab7da33b9a541290b4b2fcf21d9017a681c00e83471d25e61aee'),
    'trace':('PG11246-batch-supplied-metric-label-fixture-trace-v1','2b8a612e7317968b92f25eb20d967e55ede9939c364a868666aeabddd9059e99'),
    'contexts':('PG11245-batch-supplied-metric-label-fixture-context-v1','3729fa303a0f91b6d048ff164de20009754650529ccea80666ca1818647d1ffb'),
    'contextsPost':('PG11247-batch-supplied-metric-label-fixture-context-post-v1','f9c21953fe2e41cc507e0bd249358ef8d3fe4c21af75c9771889f73d529cb817'),
    'tracePost':('PG11248-batch-supplied-metric-label-fixture-trace-post-v1','483ad212397453b94b22e068a768ed51be7c503b586faea5b64685a4c3e83372')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11242-batch-supplied-metric-label-fixture-static-v1/manifest.json'
    static_sha = 'daf9fa3dd62ebebe03884b3e729628f74672e212a6873ce63ddef0ffb8a397f2'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2171_Batch供給metric label三Test同値fixture仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2172_Batch供給metric label三Test実行結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1904'],relatedYkt=['YKT-1655'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent SS supplied restart/integrity enums/labels/failure/null/owner vectors; F/E/S/aborted0',
        actual=dict(tests=30,suites=3,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        selectedValueMainUnits=measurement['selectedValueMain'],completeBatchCounters=post['bundleCounters'],completeBatchFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=9,
        sourceLocalContextsReviewed=8,unclassifiedComparable=1,residualApplicability='RAW9_RETAINED_COMPARABLE1_UNCLASSIFIED_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


