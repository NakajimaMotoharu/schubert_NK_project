"""Bind original86 and new3 full-payload owner-guard tests, exact source and three covered Main classes and incomplete whole coverage."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11392-full-payload-guard-completion-v1'
SOURCE = '4aee5c4b73ffae5426e0cc5d15fc928e06ece7b8'
PINS = {
    'normal':('PG11380-full-payload-guard-six-compile-v1','f9691978776defaba64743818d99b493a80ab4f36b1cd30bae3eee542ab55be2'),
    'recoveredOriginalPt':('PG11382-full-payload-guard-host-v1','a11545c458aad86980ff035f5b1609bcd62a341ddc0328dc85fd1140e162a080'),
    'post':('PG11386-full-payload-guard-post-v1','11828d8e99e55d282d39b804331e3aff8fb83a4f6c396c4697fb0138d30d75c9'),
    'trace':('PG11388-full-payload-guard-trace-v1','0a6661a9c95aa9d8ede93cdfe106078a4084d9fcf418fa526d49cbb31d944a23'),
    'contexts':('PG11387-full-payload-guard-context-v1','05d0ea5697dfe458af05045250467e076cda73da892e068113e8a142782c3321'),
    'contextsPost':('PG11389-full-payload-guard-context-post-v1','93ae0b82507de121a9cf34acbb041026319c7a8f6e1b3288c53bf039780652a4'),
    'tracePost':('PG11390-full-payload-guard-trace-post-v1','55b878db23e5d832bce5695ca4816de5ed4dfebc08c9d133d6d8b0d586260bb8')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11384-full-payload-guard-static-v1/manifest.json'
    static_sha = '075bc441fc602c77dfa0b6d7cb6eadcbf4c570893655850f6cb6140c47841a09'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2195_full payload helper・owner例外保全PGPT仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2196_full payload helper・owner例外保全結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1910'],relatedYkt=['YKT-1659'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent SS standard-source owner/retry/identity/order and self-JVM public MXBean vectors; original assertions/deadlines retained; F/E/S/aborted0',
        actual=dict(tests=89,originalMethods=86,addedIndependentMethods=3,suites=3,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        artifactMeasurements=measurement,completeArtifactsFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=39,
        sourceLocalContextsReviewed=30,unclassifiedRaw=9,residualApplicability='RAW39_CONTEXT30_DUPLICATE8_COMPARABLE1_UNCLASSIFIED_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


