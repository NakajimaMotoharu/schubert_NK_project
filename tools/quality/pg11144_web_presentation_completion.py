"""Join fixed source, original request case results and complete API misses; no execution."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11144-web-presentation-completion-v1'
SOURCE = '497dea5e49082d063d1c41e5e17999a473db6c91'
PINS = {
    'normal':('PG11132-web-presentation-six-compile-v1','6ba6867e803958aa47837d6628faeecdf42917be8d23bff7a38b5e1b18579eee'),
    'recoveredOriginalPt':('PG11134-web-presentation-host-v1','a62023de0da39ab2050e1984e3f781ac74b14979d685af187b8433e4250e2299'),
    'post':('PG11138-web-presentation-post-v1','3bb27a2ab2c5da7500ffb7c86e5395fc05a319c2cf28602b3c9876d01413f3c7'),
    'trace':('PG11140-web-presentation-trace-v1','bc245f1eecf17ac7e2aac6c01025c336a994aace8154e64d4580788f2d7d519e'),
    'contexts':('PG11139-web-presentation-context-v1','b625b3a26cbe109f4b5ddfddc58fa3b4e2a0461e78f0d87efba670552e24c0c0'),
    'contextsPost':('PG11141-web-presentation-context-post-v1','0c7d9cff1b0bc6c376573f4a5e4d176edf2b11ce7f14d2ca3278db84769cf797'),
    'tracePost':('PG11142-web-presentation-trace-post-v1','892380873ec2f9ce8f25ae947ad4cdddfc51b6baa510aa8300c3d0bd24b1bd0e')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11136-web-presentation-static-v1/manifest.json'
    static_sha = 'abe48dfe23f7b14485638cf467ba3593df309e84e2780836b295f04729b9345e'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2153_Web mock表示境界四Test同値fixture PGPT仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2154_Web mock表示境界四Test実行結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-WEB-001','NK-WEB-002'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1899'],relatedYkt=['YKT-1650'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original UI/SS header, URI literal/null/UTF8, UUID identity and Login DOM/name/message/fixture-CSRF expectations; F/E/S/aborted0',
        actual=dict(tests=15,suites=4,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        selectedValueMainUnits=measurement['selectedValueMain'],completeWebCounters=post['bundleCounters'],completeWebFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=5,
        sourceLocalContextsReviewed=5,residualApplicability='RAW5_RETAINED_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


