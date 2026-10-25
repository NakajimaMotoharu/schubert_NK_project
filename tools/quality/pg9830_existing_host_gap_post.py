"""Independent set/hash/counter gap validation and two explicit document bridges; no target replay."""
from collections import Counter
import json
from pathlib import Path
import zipfile
import g07_host_class_provenance_inputs as data
import pg9828_existing_host_gap_map as parsed
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
OUT = data.BASE / 'PG9830-existing-host-gap-post-v1'
CHANGED = {
    'api:dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime$1.class',
    'api:dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime.class',
    'api:dev/codex/schubert/nk/api/bootstrap/ApiManagementServer.class',
    'api:dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.class',
    'api:dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReport.class',
    'web:dev/codex/schubert/nk/web/bootstrap/WebHttpServer.class',
    'web:dev/codex/schubert/nk/web/bootstrap/WebProcessLifetime.class',
    'web:dev/codex/schubert/nk/web/bootstrap/WebManagementServer.class',
    'web:dev/codex/schubert/nk/web/bootstrap/WebNativeRuntime.class'}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    main_path = data.BASE / 'PG9828-existing-host-gap-map-v1/manifest.json'
    main_sha = 'cd198bf12902c3d14d7f4f72ca436a2034c27b6c76a81dea1027aab4f080b627'
    main = data.read_checked(main_path,main_sha)
    assert main['actualExit'] == 0 and main['source'] == SOURCE and not main['currentCoverageComputed']
    rows = data.read_checked(main_path.parent / 'physical-class-gap-map.json',main['physicalGapMapSha256'])
    sources = data.read_checked(main_path.parent / 'delta-source-followup-index.json',main['sourceFollowupIndexSha256'])
    assert len(rows) == len({r['physicalKey'] for r in rows}) == 1843
    old = data.read_checked(data.BASE / 'PG6930-current4222-cases/qualification.json',main['historicalQualificationSha256'])
    normal = data.read_checked(data.BASE / 'PG9812-cleanup-values-six-compile-v1/manifest.json',main['normalManifestSha256'])
    current = {}
    for module,value in normal['jars'].items():
        path = Path(value['path'])
        assert data.sha(path.read_bytes()) == value['sha256']
        with zipfile.ZipFile(path) as archive:
            current.update({module + ':' + name:data.sha(archive.read(name)) for name in archive.namelist() if name.endswith('.class')})
    assert {r['physicalKey']:r['currentSha256'] for r in rows} == current
    assert {r['physicalKey'] for r in rows if r['byteState'] == 'CHANGED_BYTE'} == CHANGED
    assert {r['physicalKey'] for r in rows if r['byteState'] == 'ADDED'} == set(current) - set(old['allPhysicalMainSha256'])
    same = {k for k,h in current.items() if old['allPhysicalMainSha256'].get(k) == h}
    assert {r['physicalKey'] for r in rows if r['byteState'] == 'SAME_BYTE'} == same and len(same) == 1660
    assert all(r['historicalCounters'] == old['allActualClassCounters'].get(r['physicalKey'],{}) for r in rows)
    missing = Counter(r['physicalKey'].split(':')[0] for r in rows if any(v['missed'] for v in r['historicalCounters'].values()))
    assert missing == Counter(api=5,batch=97,bootstrap=5,web=2)
    assert all(r['currentDynamicQualification'] == 'NOT_EVALUATED_NO_SOURCE_TRANSFER' for r in rows)
    no_literal = {Path(p).name for p,v in sources.items() if v['publicFollowupMatchCount'] == 0}
    assert no_literal == {'ApiMetricCatalog.java','ApiServiceMetricBinding.java'}
    bridges = []
    for simple,spec_name,spec_sha,result_name,result_sha,proof_name,proof_sha in (
        ('ApiMetricCatalog','1773_ApiApprovedPolicy_単体テスト仕様.md','bc4d155f08115cafb72460a393c8569c3ab50cfde8d163a4fbb1b341262f9a0a',
         '1774_ApiApprovedPolicy_実行結果・追跡.md','0380933c8d89cdbea93756ced0d138179bb5f4f096650dcc802e620aa7cb5f6a',
         'PG8442-api-approved-policy-fixed-post-v1','342871a5bc73d68f190014cf3b98ee146f9820c3c76bf42cf77814c1edc1725c'),
        ('ApiServiceMetricBinding','1852_APIServiceOutboxMetadata_製造・単体仕様.md','68a783526fe57c1e17b0f794afa1d491a46103413d680ec546a11866c5a011fc',
         '1853_APIServiceOutboxMetadata_実行結果・残依存.md','11b597dff8bfd29b34780aca34545bc1a38b49686fa9e9b66e512042c73c049e',
         'PG9032-api-service-post-v1','4585f25047cd5f657152facf8486a44a69fe73c67d17345b864cd61e3965a358')):
        spec,result = data.BASE.parents[1] / spec_name,data.BASE.parents[1] / result_name
        assert data.sha(spec.read_bytes()) == spec_sha and data.sha(result.read_bytes()) == result_sha
        proof = data.read_checked(data.BASE / proof_name / 'manifest.json',proof_sha)
        subject = 'dev/codex/schubert/nk/api/monitoring/' + simple
        path = 'src/schubert-nk-api/src/main/java/' + subject + '.java'
        assert spec_name.split('_')[0] in (ROOT / path).read_text()
        assert proof['actualExit'] == 0 and proof['source'] != SOURCE
        assert proof['sourceFiles'][path] == data.sha((ROOT / path).read_bytes())
        assert proof['physicalClasses'][subject + '.class'] == current['api:' + subject + '.class']
        counters = proof['executableClasses'][subject]['counters']
        assert set(counters) == {'LINE','METHOD','CLASS','BRANCH'} and all(v['missed'] == 0 for v in counters.values())
        bridges.append(dict(subject=path,spec=spec_name,specSha256=spec_sha,result=result_name,resultSha256=result_sha,
            proof=proof_name,proofSha256=proof_sha,historicalProofSource=proof['source'],sameSourceTextAndClassByte=True,
            priorDynamicQualificationNotTransferred=True,newMissingImplementationInferred=False))
    assert parsed.selftest() == 10
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    verify(invocation)
    OUT.mkdir()
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,gapMapManifestSha256=main_sha,
        fixedChangedPhysicalKeys=sorted(CHANGED),sameClassBytes=1660,addedClassBytes=174,changedClassBytes=9,
        historicalMissesByModule=dict(missing),literalNoMatchCount=2,explicitExistingDocumentBridges=bridges,
        nextIndependentCandidate='Eight unresolved source-owner fixtures: static consumer/responsibility review only, no reflection or JDBC execution',
        originalToolSyntaxFailureSha256='85916d8304088952dc0d703d6a907045b6b58ea728e99cd72c5541b0a145d4a8',
        originalSyntaxFailureEntryNotRun=True,counterSchemaVectors=10,productTestsExecuted=0,
        oldSuccessTransferred=False,coverageUnion=False,actualExternalOperations=0,whole451Accepted=False,
        wholeG01Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT / 'manifest.json',result)
    print(json.dumps(dict(actualExit=0,historicalMissClasses=109,currentPhysicalClasses=1843,explicitBridges=2,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
