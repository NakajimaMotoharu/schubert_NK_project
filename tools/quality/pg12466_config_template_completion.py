"""Bind original four template tests to current bytecode/resources, no Main coverage credit."""
from pathlib import Path
import datetime as dt
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind
from pg9978_plain_core_quality_post import test_classes
from pg9906_user_query_oracle_source_post import jar_classes
from pg11929_storage_fixture_class_metadata import parts, selftest

SOURCE = 'd6c01d3aed6bd1b546b6f5989fe80705e6e1262f'
OUT = data.BASE/'PG12466-config-template-completion-v1'
PINS = {
    'normal':('PG12450-config-template-six-compile-v1','face6e2196f8345f8ba51f4e1d29ff10df42231737e801e109d8f0e32b6d43f2'),
    'host':('PG12452-config-template-host-v1','1e31b5148cfb6eb769ad08f15435b44bc34607c4e775594462861793822085e9'),
    'static':('PG12454-config-template-static-v1','91308d49aaeea62224bdfb75eafcec99a62e6ea5ff7daa35dc8d0bf4e7f2c3bb'),
    'post':('PG12456-config-template-post-v1','5ee8066c74ce84a6f02c82a96fb3685dc47f56d91fbfb3a05634931c430ed429'),
    'trace':('PG12458-config-template-trace-v1','95d2b841403afa883e9c99e4cbfa903f2e14d46131e72b7a75a0addbd179b425'),
    'tracePost':('PG12461-config-template-trace-post-v2','d570afd1a0633018eec27b861035774e334376a6124cb15b317730971e942052'),
    'delta':('PG12462-current-config-template-delta-v1','2236248507325db831cd9af306660cdb5f251f21683118b9c80b72ac3d780b0f'),
    'deltaPost':('PG12464-current-config-template-delta-post-v1','d7b109965ed1eb4a30e1f52c697c191e65c9623c23b7a88cc004d67eb1c247e3')}


def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    bound = bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions'] == 4 and host['actualExit'] == 0 and not host['oldExecUnion']
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    previous = data.read_checked(data.BASE/'PG12406-batch-runtime-six-compile-v1/manifest.json','f38a16bb22d8c7bb4ab62000a765646569396527f78bb0949773ef8ab43ca8b3')
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    old,new = test_classes(previous),test_classes(normal)
    assert set(old) == set(new) and len(new) == 1962
    changed = [key for key in old if old[key] != new[key]]
    assert len(changed) == 2
    code_debug = []
    for role,entry in changed:
        a = parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b = parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        assert role == 'batch' and b['model']['sourceFile'] == 'ConfigurationTemplateContractTest.java'
        code_debug.append(dict(role=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    static = values['static']
    assert static['actualExit'] == 0 and all(r['findings'] == r['processingErrors'] == 0 for r in static['reports'].values())
    inverse = data.read_checked(data.BASE/'PG12448-config-template-source-post-v1/manifest.json','6ec6102a79fe2959c4c7b2e303fed50b5b2db730219fa9d0459cca9cb1267a2b')
    assert inverse['metadataNegativeVectors'] == 22 and inverse['allOriginalRawTokensRestored']
    assert normal['begin']['inputHashes'][inverse['sourceChanges'][0]['path']] == inverse['sourceChanges'][0]['sha256']
    assert post['observedTestExecutions'] == post['originalMethods'] == 4 and post['newMethods'] == 0 and post['productMainExecuted'] is False
    assert post['publicResourceCount'] == 7 and post['publicResourceNegativeVectors'] == 6
    measure = post['artifactMeasurements']
    assert set(measure) == {'batch'} and measure['batch']['completeClasses'] == 645 and not measure['batch']['selectedValueMain']
    assert all(c['covered'] == 0 for c in measure['batch']['bundleCounters'].values())
    crc = measure['batch']['executedTestCrc64']
    assert crc == {'dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest':'4b510c81a8d50d0a','dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest$Scalar':'dcfb5bc30c44d515'}
    assert not host['begin']['requiredClassDefinitions'] and not host['begin']['eligibilityClosureSourceHashes']
    assert not list(Path(host['begin']['testCwd']).iterdir())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in host['begin']['publicResourceCopies'].items())
    spec = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2336_公開設定Template七指摘_単体テスト仕様書.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2337_公開設定Template七指摘_製造単体結果.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'code-debug.json',dict(source=SOURCE,classes=code_debug,structuralReaderVectors=selftest(),meaningProof='Independent complete original token inverse; exact current four methods/resources/Test CRC; no Main execution'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,tests=host['begin']['cases'],actual=dict(tests=4,suites=1,originalMethods=4,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),newTestIds=[],specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1974','BUG-1975'],relatedYkt=['YKT-1722','YKT-1723'],implementationDecision='PG-D742',codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,testClassesChanged=2,otherTestClassesUnchanged=1960,executedTestCrc64=crc,publicResources=7,publicResourceNegativeVectors=6,productMainExecuted=False,mainCoverageQualification='NOT_APPLICABLE_NO_PRODUCT_MAIN_EXECUTED',wholeArtifactCoverage100=False,rawStatic=0,sourceRawCorrections=7,sourceDerivedRaw=8546,actualSecretCount=None,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
