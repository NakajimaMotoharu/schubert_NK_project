"""Join fixed source, original request case results and complete API misses; no execution."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11170-api-metric-fixture-completion-v1'
SOURCE = 'aafcc38d2d48627e10f816dd45bfaeb20bf5e415'
PINS = {
    'normal':('PG11158-api-metric-fixture-six-compile-v1','580ccce1abaccdd002433ac52eb674c755e3911a038669e0d65d6fafff78ae7c'),
    'recoveredOriginalPt':('PG11160-api-metric-fixture-host-v1','d05927e75f8c56a1bd639ba2a2e49c511d80f46f9e773daa05ed80466670082c'),
    'post':('PG11164-api-metric-fixture-post-v1','db7bc3836bfffbced40d486ba8de03f8a0483881c1c5d74eab8d62c872c29c98'),
    'trace':('PG11166-api-metric-fixture-trace-v1','d6b06246b2ad94e41e2c611e9d66feb163ea0ca8dbecd6ce9f15d75de57f80dc'),
    'contexts':('PG11165-api-metric-fixture-context-v1','3b02041b948f03e6993b9bf2603bf943597c252bd8e0375ee5e5c12b3a761813'),
    'contextsPost':('PG11167-api-metric-fixture-context-post-v1','fd3ac323594856c0d1b417d259957e845907bdfabe3c96c7c8fa890c458d009c'),
    'tracePost':('PG11168-api-metric-fixture-trace-post-v1','1148062c569953c5f3985a8d7801488b43f940eba040dcb21646b87251764135')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11162-api-metric-fixture-static-v1/manifest.json'
    static_sha = 'd5e5db629b48946657e44567fbfc37c2281ff19a8af5d3a879809b0bc89d7177'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2157_API供給メトリクス四Test同値fixture PGPT仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2158_API供給メトリクス四Test実行結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001','NK-MON-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1900'],relatedYkt=['YKT-1651'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent SS layout/address/stage/result/CDF/scalar/failure/owner vectors; F/E/S/aborted0',
        actual=dict(tests=34,suites=4,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        selectedValueMainUnits=measurement['selectedValueMain'],completeApiCounters=post['bundleCounters'],completeApiFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=12,
        sourceLocalContextsReviewed=12,residualApplicability='RAW12_RETAINED_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


