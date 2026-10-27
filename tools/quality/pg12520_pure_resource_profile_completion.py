"""Bind original34 pure resource/profile/public value tests and exact current source/counters."""
from pathlib import Path
import datetime as dt
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind
from pg9978_plain_core_quality_post import test_classes
from pg9906_user_query_oracle_source_post import jar_classes
from pg11929_storage_fixture_class_metadata import parts, selftest

SOURCE = 'c099786934c864f31a6fb520184366c22c84f6ea'
OUT = data.BASE/'PG12520-pure-resource-profile-completion-v1'
PINS = {
    'normal':('PG12500-pure-resource-profile-six-compile-v1','4927aa643bcd905142e5fb4091bfb9050570843435216679d1a21bd9214bd06c'),
    'host':('PG12502-pure-resource-profile-host-v1','2ddb3ff1cfc6b145dc3a785ab8e9067243d694f4fd57a33e7899ce249998d652'),
    'post':('PG12506-pure-resource-profile-post-v1','da60d127406d686a74b23eb3300411c455cb88c21d0a9f53d401230974dadd87'),
    'context':('PG12508-pure-resource-profile-context-v1','36f949bf42338516cef966581451c0d8294054518606e2888cad53df47f51719'),
    'contextPost':('PG12510-pure-resource-profile-context-post-v1','e82716db72a0148c01d8df05ecf122cb3377893557be6933fa87e2cbd70b3b80'),
    'trace':('PG12512-pure-resource-profile-trace-v1','34a6818a534b3749df66d499d10fde74dbbc783a24014e118332ead636291734'),
    'tracePost':('PG12514-pure-resource-profile-trace-post-v1','e358fe086e331650206974583be5d891c443c3e90f13255af9e9daafcb9699d2'),
    'delta':('PG12516-current-pure-resource-profile-delta-v1','81475aec82b3f079d7c18081bb77369abd56de9568133479bb05646277144ea1'),
    'deltaPost':('PG12518-current-pure-resource-profile-delta-post-v1','20c5c03dcf7ad375be7f07cb1547177d8ed1367d446450d1c4c1142404439bea')}



def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    bound = bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions'] == 34 and host['actualExit'] == 0 and not host['oldExecUnion']
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    previous = data.read_checked(data.BASE/'PG12476-enum-catalog-six-compile-v1/manifest.json','b94f82650e819d85a09fc6edfa0fe0f6fa01a04fd021ce13a5930602150952fe')
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    old,new = test_classes(previous),test_classes(normal)
    assert set(old) == set(new) and len(new) == 1962
    changed = [key for key in old if old[key] != new[key]]
    assert len(changed) == 6
    code_debug = []
    for role,entry in changed:
        a = parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b = parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        assert role in ('batch','bootstrap','storage') and b['model']['sourceFile'] in {'ResourceScopeTest.java','FactoryResourceScopeTest.java','FixedNativeCoverageProfileTest.java','ObservationValueRedactionTest.java'}
        code_debug.append(dict(role=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    static = data.read_checked(data.BASE/'PG12504-pure-resource-profile-static-v1/manifest.json','133577cdab5e74deceb505cca099830b4b06afc1800fd986efc372031e74ef04')
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings']==9 and static['reports']['checkstyle']['findings']==0 and all(r['processingErrors']==0 for r in static['reports'].values())
    inverse = data.read_checked(data.BASE/'PG12498-pure-resource-profile-source-post-v1/manifest.json','ab5c0939354865004bba4dc91abea47babe63eb1804f473ddc4f3f16b7af70d3')
    assert inverse['metadataNegativeVectors'] == 57 and inverse['allOriginalOracleTokensRestored']
    assert all(normal['begin']['inputHashes'][r['path']]==r['sha256'] for r in inverse['sourceChanges'])
    assert post['originalObservedTestExecutions']==34 and not post['oldExecUnion']
    measure=post['artifactMeasurements']
    assert set(measure)=={'batch','bootstrap','storage'} and all(measure[r]['completeClasses']==n for r,n in [('storage',80),('bootstrap',117),('batch',645)])
    assert all(not v['selectedValueFourCounters100'] and not v['wholeArtifactCoverage100'] for v in measure.values())
    direct={p:u for p,u in measure['storage']['selectedValueMain'].items() if p.rpartition('/')[2].removesuffix('.class').split('$',1)[0] in {'ResourceScope','StorageIoException'}}
    assert len(direct)==7 and all(c['missed']==0 for u in direct.values() for c in u['counters'].values())
    sums={k:sum(u['counters'][k]['covered'] for u in direct.values()) for k in ('LINE','METHOD','CLASS','BRANCH')}
    assert sums==dict(LINE=60,METHOD=8,CLASS=3,BRANCH=20)
    assert host['begin']['lexicalGuardMetadataVectors']==6
    assert not list(Path(host['begin']['testCwd']).iterdir())
    spec = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2343_Pure資源・固定profile・公開値十五是正_単体テスト仕様書.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2344_Pure資源・固定profile・公開値十五是正_製造単体結果.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'code-debug.json',dict(source=SOURCE,classes=code_debug,structuralReaderVectors=selftest(),meaningProof='Independent complete original typed token inverse57; changed33 and unchangedcompanion1 current actual34; exact pure resource/profile/value Main probe allowlist; resource family no missed, other selected methods remain uncovered'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,tests=host['begin']['cases'],actual=dict(tests=34,suites=5,originalMethods=34,changedOriginalMethods=33,unchangedCompanionMethods=1,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),newTestIds=[],specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1979'],relatedYkt=['YKT-1727'],implementationDecision='PG-D744',codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,testClassesChanged=6,otherTestClassesUnchanged=1956,resourceFamilyCounters=sums,resourceFamilyExecutableMainClasses=3,nonExecutableInterfacePhysicalClasses=4,productMainExecuted=True,mainCoverageQualification='RESOURCE_FAMILY_NO_MISSED_PROFILE_VALUE_AND_WHOLE_ARTIFACT_NOT100',wholeArtifactCoverage100=False,rawStatic=9,sourceRawCorrections=15,sourceDerivedRaw=8526,actualSecretCount=None,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
