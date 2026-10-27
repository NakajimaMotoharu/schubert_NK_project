"""Bind original32 API/Web source guard tests, exact source, two covered Main classes and incomplete whole coverage."""
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11360-api-web-source-guard-completion-v1'
SOURCE = 'd4b5507ba6a76a85c23806e5604a0278f1795f37'
PINS = {
    'normal':('PG11348-api-web-source-guard-six-compile-v1','46569de89d536e303184cd570d83f5138eb3a344abeb64f4e01160622a5482e8'),
    'recoveredOriginalPt':('PG11350-api-web-source-guard-host-v1','bc19326d1df904851b7d9a6d4970f8791d22e298d0a137ef12da41c5340a6c29'),
    'post':('PG11354-api-web-source-guard-post-v1','3928e5796bb3c0b79bdfed1afe720678ce18096ce0a9a9b514acd3c6c9492d26'),
    'trace':('PG11356-api-web-source-guard-trace-v1','5a65e479c9fb571b4e434d5a2b8d237a028020d2e994c9ead5a7b34bb719e33f'),
    'contexts':('PG11355-api-web-source-guard-context-v1','24f93b068aa960e1d488607922591b76c1997a62ecd93f4717a48623c8d9b11a'),
    'contextsPost':('PG11357-api-web-source-guard-context-post-v1','93eb89d97be4a1621d67a0aa3af54c9ada11ec46494342769f6f341f15208a33'),
    'tracePost':('PG11358-api-web-source-guard-trace-post-v1','419712f059dfaa92cc92935e49626508ba0dea07c11f2bbce63bfc27a4ee33c1')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11352-api-web-source-guard-static-v1/manifest.json'
    static_sha = 'aac5877aeea4e595f71d3e7fb1e823c07490938011be0c7f2d5c6dc716794ddc'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2189_API・Web標準source owner横展開PGPT仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2190_API・Web標準source owner横展開結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1909'],relatedYkt=['YKT-1659'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent SS standard-source owner/retry/identity/order and self-JVM public MXBean vectors; original assertions/deadlines retained; F/E/S/aborted0',
        actual=dict(tests=32,suites=2,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        artifactMeasurements=measurement,completeArtifactsFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=16,
        sourceLocalContextsReviewed=12,unclassifiedRaw=4,residualApplicability='RAW16_THREAD12_CONTEXT_ONLY_COMPOSITE_GC4_UNCLASSIFIED_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


