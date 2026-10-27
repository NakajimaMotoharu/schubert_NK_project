"""Bind original44 plus two memory HTTP cleanup tests, exact source and two covered Main classes and incomplete whole coverage."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11548-memory-http-guard-completion-v1'
SOURCE = '7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
PINS = {'normal': ('PG11536-memory-http-guard-six-compile-v1', '038ace9c4a7187703381af22f7ecb5680f7b5d3adb2a07a242c579ca36019936'), 'recoveredOriginalPt': ('PG11538-memory-http-guard-host-v1', '793e7131b39cb23b41c29a3342a9695504ec9cd1c526a0ee758b813ab20b9216'), 'post': ('PG11542-memory-http-guard-post-v1', '507cd1d954721a3d225cc33c72b3b44ae75efe511b48afa9030d63613a191124'), 'contexts': ('PG11543-memory-http-guard-context-v1', 'db8f662a118b6e798b982992cc70c6819366156e5c5974f79bd91238071680b6'), 'contextsPost': ('PG11545-memory-http-guard-context-post-v1', '8707d944c0306c9dbc20b62556630613d109697618adf7c20c9b753874c04653'), 'trace': ('PG11544-memory-http-guard-trace-v1', '904aa522ea4b71c5c09636e8cedd3991aa284e2d3f2dba821744a88e7e57a058'), 'tracePost': ('PG11546-memory-http-guard-trace-post-v1', '53b6bc797286a9ccf95f6640f6332a3b7641bd21d808ff3555c74ab2e4729840')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11540-memory-http-guard-static-v1/manifest.json'
    static_sha = 'b853cc3070e3a836a251a2118fdeb8ef038680be336e929fde1b604fb385314b'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2221_メモリHTTP Exchange例外保全PGPT仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2222_メモリHTTP Exchange例外保全結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1921','BUG-1922'],relatedYkt=['YKT-1670','YKT-1671'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent fixed GET/raw-path/405404/ready text/header/status/UTF8 byte lengths/Throwable identity/borrowed-write close and typed getter vectors; F/E/S/aborted0',
        actual=dict(tests=46,suites=2,newProductTestIds=2,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        artifactMeasurements=measurement,completeArtifactsFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=54,oldDiagnostics=52,newDiagnostics=2,
        sourceLocalContextsReviewed=54,unclassifiedRaw=0,residualApplicability='RAW54_LOGICAL_MEMORY_GUARDS50_IMMEDIATE_CLOSE2_NEW_ORACLE2_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


