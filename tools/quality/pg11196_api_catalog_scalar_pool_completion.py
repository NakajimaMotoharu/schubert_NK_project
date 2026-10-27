"""Join fixed source, original request case results and complete API misses; no execution."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11196-api-catalog-scalar-pool-completion-v1'
SOURCE = '5eeb36dd1995ebbca2eb3ba7be30b4c4e1b69b81'
PINS = {
    'normal':('PG11184-api-catalog-scalar-pool-six-compile-v1','b969eabaf6bc2a4ca11e09532164925246302c919c2cd2e6000b63fb42984a7b'),
    'recoveredOriginalPt':('PG11186-api-catalog-scalar-pool-host-v1','c9eb44f12855b2c132cfe65c461b018b9abf0d230e61082ceb506b73d9564ac5'),
    'post':('PG11190-api-catalog-scalar-pool-post-v1','f391e0c02c03d0b716e9f47a13d4cb4acb2bf00df67f5db6ad781cf2e33af8a7'),
    'trace':('PG11192-api-catalog-scalar-pool-trace-v1','11dc1bc6c678115298de68b7be7d0fb7b81fd42f2e1a94d352347515d8d05c81'),
    'contexts':('PG11191-api-catalog-scalar-pool-context-v1','d661d1e0f7468ba35c20d249153a2af29d58533c3ac211c08e1c81e40d05fd5c'),
    'contextsPost':('PG11193-api-catalog-scalar-pool-context-post-v1','8d83e5ba41b8ca3396868ae865e289bd6743707574d007f273ea3d070b113559'),
    'tracePost':('PG11194-api-catalog-scalar-pool-trace-post-v1','47c91d76e81e49d3ace74337bb4b10d3005af7558381213e3e6d8b3052a42204')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11188-api-catalog-scalar-pool-static-v1/manifest.json'
    static_sha = '971a69f774393a5e92325bd23ca52880338ef31e7828c8b64f9b53e474bc61b9'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2161_API catalog scalar pool三Test同値fixture仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2162_API catalog scalar pool三Test実行結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001','NK-MON-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1901'],relatedYkt=['YKT-1652'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent SS labels/text/NaN/scalar/Counts/failure/identity/owner vectors; F/E/S/aborted0',
        actual=dict(tests=46,suites=3,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        selectedValueMainUnits=measurement['selectedValueMain'],completeApiCounters=post['bundleCounters'],completeApiFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=10,
        sourceLocalContextsReviewed=8,unclassifiedComparable=2,residualApplicability='RAW10_RETAINED_COMPARABLE2_UNCLASSIFIED_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


