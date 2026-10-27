"""One-source original2/new1 dependency contracts and five Test style fixes, no Main coverage credit."""
from pathlib import Path
import datetime as dt
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind
from pg9978_plain_core_quality_post import test_classes
from pg9906_user_query_oracle_source_post import jar_classes
from pg11929_storage_fixture_class_metadata import parts, selftest

SOURCE = '1be156b6ebb139713db31a561b8b024972975471'
OUT = data.BASE/'PG12428-batch-runtime-completion-v1'
PINS = {
    'normal':('PG12406-batch-runtime-six-compile-v1','f38a16bb22d8c7bb4ab62000a765646569396527f78bb0949773ef8ab43ca8b3'),
    'host':('PG12408-batch-runtime-host-v1','35387e38bb66de3240eb74086666fc6dd91cd8b68a5ee511b364dc9fc2d9d006'),
    'post':('PG12412-batch-runtime-post-v1','490c60f253fb284855962bd4832a7ad3dc1cbedb6f3b52457f9fdd4d5fd9d6d0'),
    'trace':('PG12418-batch-runtime-trace-v1','e216153b1e7151ef811c19aa839e1d3aa6f4b0f74bd0ea929d199bed94bbc85f'),
    'tracePost':('PG12421-batch-runtime-trace-post-v2','db6689a2b8a4f4d062017e7bc7b4b2647b6f75ebfad52ac48f46e176ce34772f'),
    'delta':('PG12424-current-batch-runtime-delta-v1','466a2d8c537975bfee8de7c83633f38ce33dffb319c9fd326f82d8e248362268'),
    'deltaPost':('PG12426-current-batch-runtime-delta-post-v1','f2cf2bfb976182027f93fd5b320e12da9334abf47cb9671c0f53fed0ad3cccf5')}

def main():
    invocation = capture(__file__);assert not OUT.exists()
    bound = bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions'] == 3 and host['actualExit'] == 0 and not host['oldExecUnion']
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    previous = data.read_checked(data.BASE/'PG12378-pool-batch-six-compile-v1/manifest.json','27e5dafc18e19fb5e29edd96958a5ba2f05da01611aa12b1ca8208735eb52b75')
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    old,new = test_classes(previous),test_classes(normal)
    assert set(old) == set(new) and len(new) == 1962
    changed = [key for key in old if old[key] != new[key]];assert len(changed) == 1
    role,entry = changed[0]
    a = parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
    b = parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
    assert b['model']['sourceFile'] == 'BatchRuntimeDependencyTest.java'
    static = data.read_checked(data.BASE/'PG12410-batch-runtime-static-v1/manifest.json','bb56b5c564bea635bea8d9cd167330f249dc53996b4c7892432bad9e98f43d93')
    assert static['source'] == SOURCE and static['actualExit'] == 0 and all(r['findings'] == r['processingErrors'] == 0 for r in static['reports'].values())
    oracle = data.read_checked(data.BASE/'PG12404-batch-runtime-oracle-source-post-v1/manifest.json','252f1348b9bfc70035cfb52c0c4fb464383e81e07a9c1de9bfdff64e3849f905')
    literal = data.read_checked(data.BASE/'PG12405-batch-runtime-literal-source-post-v2/manifest.json','3ff685e47422a09a15eb51f067e675b715a8854d6d14406e5d9e327326ea435d')
    assert oracle['metadataNegativeVectors'] == 6 and literal['metadataNegativeVectors'] == 15 and literal['oracleSourcePostSha256'] == '252f1348b9bfc70035cfb52c0c4fb464383e81e07a9c1de9bfdff64e3849f905'
    assert literal['sourceChanges'][0]['oracleIntermediateSha256'] == oracle['sourceChanges'][0]['sha256']
    assert normal['begin']['inputHashes'][literal['sourceChanges'][0]['path']] == literal['sourceChanges'][0]['sha256']
    assert post['observedTestExecutions'] == 3 and post['originalMethods'] == 2 and post['newMethods'] == 1 and post['productMainExecuted'] is False
    measure = data.read_checked(data.BASE/'PG12412-batch-runtime-post-v1/measurement.json',post['measurementSha256'])
    assert set(measure) == {'batch'} and measure['batch']['completeClasses'] == 645 and not measure['batch']['selectedValueMain']
    assert all(c['covered'] == 0 for c in measure['batch']['bundleCounters'].values())
    assert not host['begin']['requiredClassDefinitions'] and not host['begin']['eligibilityClosureSourceHashes']
    assert not list(Path(host['begin']['testCwd']).iterdir())
    spec = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2331_Batch標準SDK依存Oracle是正_単体テスト仕様書.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2332_Batch標準SDK依存Oracle是正_製造単体結果.md'
    verify(invocation);OUT.mkdir()
    data.write(OUT/'code-debug.json',dict(source=SOURCE,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256'],structuralReaderVectors=selftest(),meaningProof='Independent original token preservation plus explicit approved SDK oracle additions; five same-value inverse to intermediate source; actual current original2/new1'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,tests=host['begin']['cases'],actual=dict(tests=3,suites=1,originalMethods=2,newProductTestIds=1,failures=0,errors=0,skipped=0,aborted=0),newTestIds=['PT-BAT-283C'],specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1970','BUG-1971','BUG-1972','BUG-1973'],relatedYkt=['YKT-1718','YKT-1719','YKT-1720','YKT-1721'],implementationDecision='PG-D740',codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,testClassesChanged=1,otherTestClassesUnchanged=1961,productMainExecuted=False,mainCoverageQualification='NOT_APPLICABLE_NO_PRODUCT_MAIN_EXECUTED',wholeArtifactCoverage100=False,rawStatic=0,sourceRawCorrections=5,sourceDerivedRaw=8553,originalExpectationChangedOnlyForAlreadyApprovedTwoSdkCoordinates=True,actualSecretCount=None,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
