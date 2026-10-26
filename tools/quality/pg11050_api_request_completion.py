"""Join fixed source, original request case results and complete API misses; no execution."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11050-api-request-completion-v1'
SOURCE = '9b255cbe300d1feffeeee076cfa5af318c9b1bb1'
PINS = {
    'normal':('PG11038-api-request-six-compile-v1','5f2d2363b5d3ddaf1c61b59e096ffe5705725b332dcf4324381181c1c6c90e7b'),
    'recoveredOriginalPt':('PG11043-api-request-original-recovery-v1','9e65b9f3b7c025054d56155aa16ed9f8054df8c04d5a5c9afff1bbf107548dd9'),
    'post':('PG11044-api-request-post-v1','5a6444609c3ce10bc16a40cb024b2b02510cb9b6fae3e96087edf4b37c052c4a'),
    'trace':('PG11046-api-request-trace-v1','50c22418669fcc59bb38939cf9cda03dedaab07cc86932c9c45faba05248a861'),
    'tracePost':('PG11048-api-request-trace-post-v1','25dba645994d3fb856a3509f6cc95bc78af079970d699f311cc95c07b4f7a3e6')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11040-api-request-static-v1/manifest.json'
    static_sha = '56546bff6f2b5922c20024bb24354ab54f79ad45d58a69b95b3ce320dd778d9e'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2141_API request四Test同値fixture・私有名PGPT仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2142_API request四Test実行結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-SCN-001','NK-MED-001','NK-QRY-001','NK-NTF-001','NK-QST-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1889','BUG-1890','BUG-1891'],relatedYkt=['YKT-1640','YKT-1641','YKT-1642'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original UI234235236 byte golden and independent SS324 LP/JCE vectors; F/E/S/aborted0',
        actual=dict(tests=16,suites=4,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=1,originalTargetJvmExit=0,recoveryOnly=True,
        selectedRequestMainUnits=measurement['selectedRequestMain'],completeApiCounters=post['bundleCounters'],completeApiFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=17,
        residualApplicability='UNCLASSIFIED',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
