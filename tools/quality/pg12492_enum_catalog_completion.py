"""Bind original two enum catalog tests to current bytecode and exact enum counters."""
from pathlib import Path
import datetime as dt
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind
from pg9978_plain_core_quality_post import test_classes
from pg9906_user_query_oracle_source_post import jar_classes
from pg11929_storage_fixture_class_metadata import parts, selftest

SOURCE = '6929166ee735effb5cae211e1f4cfe44f0b97a0a'
OUT = data.BASE/'PG12492-enum-catalog-completion-v1'
PINS = {
    'normal':('PG12476-enum-catalog-six-compile-v1','b94f82650e819d85a09fc6edfa0fe0f6fa01a04fd021ce13a5930602150952fe'),
    'host':('PG12479-enum-catalog-host-v2','27f9a83d3724909768a1d8ada251a0f60c8492a880fe68549aaac9933a63d637'),
    'static':('PG12480-enum-catalog-static-v1','2325f28cc6f45e6c8b1191902b5e3370a3c7bbd3a7935eee5c1b551a3ab417bc'),
    'post':('PG12482-enum-catalog-post-v1','acef5bf0b2d633aec473b3c5eb2a972711b081bb08bd8b2bc8849623a7eb3cd5'),
    'trace':('PG12484-enum-catalog-trace-v1','66aa004399ee507c8214996c12a487097b09b2f8dcc1e7188df3f9a2e0e4f922'),
    'tracePost':('PG12486-enum-catalog-trace-post-v1','94dac775d812385ced3562e188ef4b7cd5908506f97fb59e361e212ac294366d'),
    'delta':('PG12488-current-enum-catalog-delta-v1','9514312d8850dd0205e4d5318d71288d2be5b5343c11751c4c23045cca03ccc0'),
    'deltaPost':('PG12490-current-enum-catalog-delta-post-v1','de92648d9efcd0e6d4df8427274c29bedbc5bba82f3bf493e939c08f17392ab9')}



def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    bound = bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions'] == 2 and host['actualExit'] == 0 and not host['oldExecUnion']
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    previous = data.read_checked(data.BASE/'PG12450-config-template-six-compile-v1/manifest.json','face6e2196f8345f8ba51f4e1d29ff10df42231737e801e109d8f0e32b6d43f2')
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    old,new = test_classes(previous),test_classes(normal)
    assert set(old) == set(new) and len(new) == 1962
    changed = [key for key in old if old[key] != new[key]]
    assert len(changed) == 2
    code_debug = []
    for role,entry in changed:
        a = parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b = parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        assert role in ('batch','storage') and b['model']['sourceFile'] == 'EnumValueCatalogCompatibilityTest.java'
        code_debug.append(dict(role=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    static = values['static']
    assert static['actualExit'] == 0 and all(r['findings'] == r['processingErrors'] == 0 for r in static['reports'].values())
    inverse = data.read_checked(data.BASE/'PG12474-enum-catalog-source-post-v1/manifest.json','9c6b93d2f354418cd74f59b0461171a13547e3c0a6f2246cf6c3f5bd4d01b86e')
    assert inverse['metadataNegativeVectors'] == 16 and inverse['allOriginalOracleTokensRestored']
    assert all(normal['begin']['inputHashes'][r['path']]==r['sha256'] for r in inverse['sourceChanges'])
    assert post['originalObservedTestExecutions']==2 and not post['oldExecUnion']
    measure=post['artifactMeasurements']
    assert set(measure)=={'batch','storage'} and measure['batch']['completeClasses']==645 and measure['storage']['completeClasses']==80
    assert all(v['selectedValueFourCounters100'] and not v['wholeArtifactCoverage100'] for v in measure.values())
    direct={p:u for v in measure.values() for p,u in v['selectedValueMain'].items()}
    assert len(direct)==7 and all(c['missed']==0 for u in direct.values() for c in u['counters'].values())
    sums={k:sum(u['counters'][k]['covered'] for u in direct.values()) for k in ('LINE','METHOD','CLASS','BRANCH')}
    assert sums==dict(LINE=80,METHOD=20,CLASS=6,BRANCH=8)
    assert host['begin']['lexicalGuardMetadataVectors']==6
    assert not list(Path(host['begin']['testCwd']).iterdir())
    spec = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2340_StorageBatch固定enum五是正_単体テスト仕様書.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2341_StorageBatch固定enum五是正_製造単体結果.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'code-debug.json',dict(source=SOURCE,classes=code_debug,structuralReaderVectors=selftest(),meaningProof='Independent complete original token inverse16; current original2; exact enum Main probe allowlist; six direct enums all counters no missed'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,tests=host['begin']['cases'],actual=dict(tests=2,suites=2,originalMethods=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),newTestIds=[],specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1977','BUG-1978'],relatedYkt=['YKT-1725','YKT-1726'],implementationDecision='PG-D743',codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,testClassesChanged=2,otherTestClassesUnchanged=1960,directEnumCounters=sums,directEnumMainClasses=6,syntheticDefaultFilteredPhysicalClasses=1,productMainExecuted=True,mainCoverageQualification='SIX_DIRECT_ENUM_MAIN_FOUR_COUNTERS_NO_MISSED_NOT_WHOLE_ARTIFACT',wholeArtifactCoverage100=False,rawStatic=0,sourceRawCorrections=5,sourceDerivedRaw=8541,actualSecretCount=None,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
