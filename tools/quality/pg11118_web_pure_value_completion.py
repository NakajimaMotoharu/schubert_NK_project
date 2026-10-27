"""Join fixed source, original request case results and complete API misses; no execution."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11118-web-pure-value-completion-v1'
SOURCE = '5fce2af667d8d5cdd9b67da9b02080b105848c28'
PINS = {
    'normal':('PG11106-web-pure-value-six-compile-v1','77fd485d4718416d3cb75e57e16458d2633289b432bb30a97738d326edcc364b'),
    'recoveredOriginalPt':('PG11108-web-pure-value-host-v1','1d6693db42dc71b7a719b28edc48f8e1f73b29e78aed98b24d6ec923e01bab52'),
    'post':('PG11112-web-pure-value-post-v1','811d07907c69923f43ccdfd66bbdd3e301cb7c50b03946a0e8135863354471a8'),
    'trace':('PG11114-web-pure-value-trace-v1','38722c25d90c564083df9267de3786dd0c7050834bf0c82c138a231fca258ed5'),
    'contexts':('PG11113-web-pure-value-context-v1','33b0641d03cfa5bf59029068e376ad180cbf2e1c228d4550741b2cf898b05d0c'),
    'contextsPost':('PG11115-web-pure-value-context-post-v1','8981f66ee5dfc0c865f2192d6db23bedee0c7c9435ebca5fef6e08df170a68b1'),
    'tracePost':('PG11116-web-pure-value-trace-post-v1','00f4352b8d72a853c2b28b5b7ddab067ccd75baae8a207c5038f16d32cdb637c')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11110-web-pure-value-static-v1/manifest.json'
    static_sha = 'd9fb45add999405f77dd42178b344e1da40983e46fa8c3c897088f2db5bb03d6'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2149_pure Web値三Test同値fixture PGPT仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2150_pure Web値三Test実行結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-MED-001','NK-OPS-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1897','BUG-1898'],relatedYkt=['YKT-1648','YKT-1649'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original UI232235 fixed wire and SS351 independent route fixture/cardinality/label vectors; F/E/S/aborted0',
        actual=dict(tests=24,suites=3,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        selectedValueMainUnits=measurement['selectedValueMain'],completeWebCounters=post['bundleCounters'],completeWebFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=10,
        sourceLocalContextsReviewed=9,residualApplicability='COMPARABLE1_UNCLASSIFIED_RAW10_RETAINED',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()

