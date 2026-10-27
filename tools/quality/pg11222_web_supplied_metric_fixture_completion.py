"""Bind original32 supplied Web metric tests, exact source, incomplete whole coverage and canonical Program ID."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11222-web-supplied-metric-fixture-completion-v1'
SOURCE = 'ae55baa85af2174fa01d73b62ad8899d3f44f306'
PINS = {
    'normal':('PG11210-web-supplied-metric-fixture-six-compile-v1','11fb92b0b53b9dba26b93c8aa3e08c09c6c754b1b43fca1c20767ac270666d73'),
    'recoveredOriginalPt':('PG11212-web-supplied-metric-fixture-host-v1','32bdd3586a7f872afbc147f2e92d6e3a5d06ff9f92a00b984a66ac0f7eea319e'),
    'post':('PG11216-web-supplied-metric-fixture-post-v1','4e2e884eee64d318cb2faceaceffed3e61e577bcd595943babc4e03734b22c77'),
    'trace':('PG11218-web-supplied-metric-fixture-trace-v1','7fe0887ff4775b11278d861b2f43c22c6a5ce467b4d452d6e67a3abc3a100195'),
    'contexts':('PG11217-web-supplied-metric-fixture-context-v1','35d8853adda2d4489b3a805793f09ca94de996bfe68ec7e8bdb321f492791cab'),
    'contextsPost':('PG11219-web-supplied-metric-fixture-context-post-v1','bc889d966d644be0ab9ea4a4e72f24e44edebf9ad4a560ebc38d1b25867464b8'),
    'tracePost':('PG11220-web-supplied-metric-fixture-trace-post-v1','6fedb88001cf05d5bead82a7718fffe3102cff2ae4f698fc389434af54321ae6')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11214-web-supplied-metric-fixture-static-v1/manifest.json'
    static_sha = 'e5d43bcb6925b46f46ba1f408e7d80614231f576e058fe994e702beedbe98030'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2165_Web供給metric四Test同値fixture仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2166_Web供給metric四Test実行結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1902'],relatedYkt=['YKT-1653'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent SS scalar bytes/streams/Counts/Duration/labels/failure/identity/null/owner vectors; F/E/S/aborted0',
        actual=dict(tests=32,suites=4,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        selectedValueMainUnits=measurement['selectedValueMain'],completeWebCounters=post['bundleCounters'],completeWebFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=14,
        sourceLocalContextsReviewed=14,residualApplicability='RAW14_RETAINED_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


