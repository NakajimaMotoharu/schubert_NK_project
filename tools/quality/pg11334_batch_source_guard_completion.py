"""Bind original16 Batch standard-source guard tests, exact source, one covered Main and incomplete whole coverage."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11334-batch-source-guard-completion-v1'
SOURCE = '862cce50220c6ce186c084504756a7fbb9978270'
PINS = {
    'normal':('PG11322-batch-source-guard-six-compile-v1','066e1c301187c43224e8ab120c50889ef8a832f48de3fe4406aa7e533ac14e27'),
    'recoveredOriginalPt':('PG11324-batch-source-guard-host-v1','bf9b6663633c9091069a107d82af3d7dc83548a8c86340cf453c020cd8a5d6e6'),
    'post':('PG11328-batch-source-guard-post-v1','c5ce52f97e1ef5762f071d6006b0efdc9df2801b00efb98bbd77f0707f618806'),
    'trace':('PG11330-batch-source-guard-trace-v1','91a431e8ffc0240f64f729ca7e7e6ce6894b4bab35aee82ea9f64317ff9687b0'),
    'contexts':('PG11329-batch-source-guard-context-v1','fd78b2d6728898510ce9e585e0613a0477f8fd67be8a6298ac315aad633be6f7'),
    'contextsPost':('PG11331-batch-source-guard-context-post-v1','e8ec88ebb4a1fffad43de5f3b1ff47bcc46ad54bb437bd33092ccd2e4255bce6'),
    'tracePost':('PG11332-batch-source-guard-trace-post-v1','d2388f5433da5cfc79685ef3b52fa550a1e2071cdf3de8db8b1cb8648183d2f9')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11326-batch-source-guard-static-v1/manifest.json'
    static_sha = '038ece1f7b1c1c0f04c651f829688a661788756d3c68cface349a5bda2104623'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2185_Batch標準source owner例外保全PGPT仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2186_Batch標準source owner例外保全結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1908'],relatedYkt=['YKT-1659'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent SS standard-source owner/retry/identity/order and self-JVM public MXBean vectors; original assertions/deadlines retained; F/E/S/aborted0',
        actual=dict(tests=16,suites=1,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        selectedValueMainUnits=measurement['selectedValueMain'],completeBatchCounters=post['bundleCounters'],completeBatchFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=8,
        sourceLocalContextsReviewed=6,unclassifiedRaw=2,residualApplicability='RAW8_THREAD6_CONTEXT_ONLY_COMPOSITE_GC2_UNCLASSIFIED_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


