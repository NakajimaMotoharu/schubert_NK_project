"""Bind original32 API/Web GC fixed-oracle tests, exact source and two covered Main classes and incomplete whole coverage."""
import ast
import re
import copy
import datetime as dt
from pathlib import Path
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

OUT = data.BASE/'PG11486-api-web-gc-literal-completion-v1'
SOURCE = 'd1fa07bbd145ea48854b9f2b3b8be6f0f3c99dd7'
PINS = {
    'normal':('PG11474-api-web-gc-literal-six-compile-v1','53e240a80b6c663419f8cff7ecb2199c8f36c343cfa9c072f8087ba0b3062cd2'),
    'recoveredOriginalPt':('PG11476-api-web-gc-literal-host-v1','f585cdc970f76dacbc83fbbc452988f4c38dd612146344e1302df34efeede4eb'),
    'post':('PG11480-api-web-gc-literal-post-v1','b6a3266c1a1080a60cc700c0c09616134bbc8ed190d58f129c7bcdd689f68c48'),
    'trace':('PG11482-api-web-gc-literal-trace-v1','161066f7b075e5c2107c342eeabfa6bc089c7068d45bcbc76062fb691210ef03'),
    'contexts':('PG11481-api-web-gc-literal-context-v1','06a16aa30c664c67ff9bf24005406af9ab3fc2dfd74097c58328a08ec54b6d14'),
    'contextsPost':('PG11483-api-web-gc-literal-context-post-v1','986e6fd56c232e602661eeaa714e69f7ed1f418b5a7668ae5769539985c28e6d'),
    'tracePost':('PG11484-api-web-gc-literal-trace-post-v1','bdb39b5a9571f03d6b53b4ccdaa5617504552badba6f75bd444884c797b1a066')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    bound = bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','recoveredOriginalPt','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    static_path = data.BASE/'PG11478-api-web-gc-literal-static-v1/manifest.json'
    static_sha = '1a50d80fd30b1809f89a55e0bab3d9b51100f9e89251970d71bdd78aab5a05bd'
    static = data.read_checked(static_path,static_sha)
    assert static['actualExit'] == 1 and static['source'] == SOURCE
    specification = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2211_API・Web GC同値fixture PGPT仕様.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2212_API・Web GC同値fixture結果.md'
    measurement = data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    # Generation regression guard: counts must not rewrite hexadecimal identities.
    current_tool=(data.ROOT/'tools/quality/pg11476_api_web_gc_literal_host.py').read_text()
    old_tool=(data.ROOT/'tools/quality/pg11446_gc_fake_guard_host.py').read_text()
    old_hashes=set(re.findall(r'(?<![a-f0-9])[a-f0-9]{64}(?![a-f0-9])',old_tool))
    current_hashes=set(re.findall(r'(?<![a-f0-9])[a-f0-9]{64}(?![a-f0-9])',current_tool))
    assert old_hashes-current_hashes=={'0f5f38eb4fc41cde15284301f8b57b53c4f22743004411b71ece13a60ed1edfb','ee7e93ea6dd4a8444f60778b1742d568e5f9767dae016bddd3604f9b065c8778'}
    assert current_hashes-old_hashes=={'53e240a80b6c663419f8cff7ecb2199c8f36c343cfa9c072f8087ba0b3062cd2','f307c042461dad4bc34301cc7dd5514c78c36c27cc5ad7114b0c202051a6ac3b'}
    assignments={node.targets[0].id:ast.literal_eval(node.value) for node in ast.parse(current_tool).body if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('SOURCE','NORMAL_SHA')}
    assert assignments==dict(SOURCE=SOURCE,NORMAL_SHA=PINS['normal'][1])
    # A prior registry can only identify an old snapshot with the same source and exact attributes.
    registry_path=data.BASE/'PG11460-current-gc-fake-guard-delta-v1/manifest.json'
    registry=data.read_checked(registry_path,'3fa311d080bb8aa9ba82cdaf6c0fb45cd739fe4b3131a9d5e1473fcb91c841e2')
    delta=data.read_checked(registry_path.parent/'delta.json',registry['deltaSha256'])
    plan=data.read_checked(data.BASE/'PG11470-api-web-gc-literal-plan-v2/manifest.json','85fd365b478659ece515a86a799f855b0327620b168ac8a7d7d087c1e55e1979')
    def eligible(source,row,expected):
        return source==plan['sourceBefore'] and row['path']==expected['path'] and row['attributes']==expected['attributes'] and row['id']==expected['id']
    expected=next(r for r in delta['freshRows'] if r['rule']=='AvoidDuplicateLiterals')
    assert eligible(registry['source'],expected,expected)
    bads=[]
    bad=copy.deepcopy(expected);bad['attributes']['beginline']='0';bads.append((registry['source'],bad))
    bad=copy.deepcopy(expected);bad['id']='PMD-00000';bads.append((registry['source'],bad))
    bads.append(('old-source',expected))
    assert all(not eligible(source,row,expected) for source,row in bads)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,programIds=['NK-OPS-001'],
        invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),
        specificationPath=str(specification.relative_to(data.ROOT)),specificationSha256=data.sha(specification.read_bytes()),
        resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1917','BUG-1918','BUG-1919'],relatedYkt=['YKT-1666','YKT-1667','YKT-1668'],relatedSsc=[],
        boundOriginalRuns=bound,sourceChangeCommit=SOURCE,tests=host['begin']['cases'],
        originalCommandsAndToolEnvironmentReference=str((data.BASE/PINS['recoveredOriginalPt'][0]/'manifest.json').relative_to(data.ROOT)),
        expected='Original independent SS standard-source owner/retry/identity/order and self-JVM public MXBean vectors; original assertions/deadlines retained; F/E/S/aborted0',
        actual=dict(tests=32,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,recoveryOnly=False,
        artifactMeasurements=measurement,completeArtifactsFourCounters100=False,
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=24,
        sourceLocalContextsReviewed=24,unclassifiedRaw=0,residualApplicability='RAW24_THREAD4_RETAINED_GC2_IMMEDIATE_CLOSE2_CONDITIONAL_FAKE12_NEW_FAKE4_CURRENT_WHOLE_PENDING_NOT_PT_EXEMPT',checkstyle=0,processingErrors=0,
        toolIdentityPreflight=True,priorSnapshotIdentityNegativeVectors=3,productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,
        effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta; not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()


