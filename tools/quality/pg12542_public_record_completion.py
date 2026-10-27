"""Bind current original2/new2 public diagnostic/null Tests, source/counters and filter specification."""
from pathlib import Path
import datetime as dt
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind
from pg9978_plain_core_quality_post import test_classes
from pg9906_user_query_oracle_source_post import jar_classes
from pg11929_storage_fixture_class_metadata import parts, selftest

SOURCE = '03ffd8803faf780d872d002426c599a2a0a3814f'
OUT = data.BASE/'PG12542-public-record-completion-v1'
PINS = {
    'normal':('PG12528-public-record-six-compile-v1','59a22edd2c2584134bb3f2d4a5bc3de042d007afee84f6aa8e0bd17e8a24c735'),
    'host':('PG12530-public-record-host-v1','dfc671b259a908b21f19e7aded4aed8bea611804116a6fe5e89abcae04456031'),
    'static':('PG12532-public-record-static-v1','8503bd587b5bf9116527d22f524e3e8857bd9c736201317960a12ac01fedb341'),
    'post':('PG12534-public-record-post-v1','a323962266faa692be827b8e169d837da893472cd8ae7f5c56f6b61b3ac1a2bc'),
    'trace':('PG12536-public-record-trace-v1','0d57cc989a1e3e1bccc63126cbe43307891398fe723834bfb594d32fe28fe161'),
    'tracePost':('PG12537-public-record-trace-post-v1','942757bc961a665ec10f5f282cc8738bfa0259a41afc688256a5b14bf9bb48e3'),
    'delta':('PG12538-current-public-record-delta-v1','27d85af42dce30f8aa0dbc2e316d81cdb08aaf44a1a9a922624548a3d223f0ad'),
    'deltaPost':('PG12540-current-public-record-delta-post-v1','06edaa81bc07323f32ce7dea2a7198b52d43337a4323d176e44b230ace1834de')}



def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    bound = bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    values = {k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()}
    normal,host,post = (values[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions'] == 4 and host['actualExit'] == 0 and not host['oldExecUnion']
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    previous = data.read_checked(data.BASE/'PG12500-pure-resource-profile-six-compile-v1/manifest.json','4927aa643bcd905142e5fb4091bfb9050570843435216679d1a21bd9214bd06c')
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    old,new = test_classes(previous),test_classes(normal)
    assert set(old) == set(new) and len(new) == 1962
    changed = [key for key in old if old[key] != new[key]]
    assert len(changed) == 1
    code_debug = []
    for role,entry in changed:
        a = parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b = parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        assert role == 'batch' and b['model']['sourceFile'] == 'ObservationValueRedactionTest.java'
        code_debug.append(dict(role=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    static = values['static']
    assert static['actualExit'] == 0 and all(r['findings'] == r['processingErrors'] == 0 for r in static['reports'].values())
    inverse = data.read_checked(data.BASE/'PG12526-public-record-oracle-source-post-v1/manifest.json','f5a15bcdb014618b912222b148da5d3a8033eb33fa2b0f828feb974610091437')
    assert inverse['metadataNegativeVectors'] == 16 and inverse['allOtherOriginalTokensRestored']
    assert all(normal['begin']['inputHashes'][r['path']]==r['sha256'] for r in inverse['sourceChanges'])
    assert post['originalObservedTestExecutions']==4 and post['originalMethods']==post['newMethods']==2 and not post['oldExecUnion']
    measure=post['artifactMeasurements']
    assert set(measure)=={'batch','storage'} and measure['batch']['completeClasses']==645 and measure['storage']['completeClasses']==80
    assert all(not v['selectedValueFourCounters100'] and not v['wholeArtifactCoverage100'] for v in measure.values())
    assert post['diagnosticFourCounters']==dict(LINE=20,METHOD=8,CLASS=4,BRANCH=0) and post['naturalDiagnosticBranchDenominatorZero']
    assert post['newMissingFieldVectors']==7 and inverse['newMissingFieldVectors']==7
    assert inverse['newTestIds']==post['newTestIds']==['PT-OPS-OBSDATA-003','PT-OPS-OBSDATA-004']
    assert not list(Path(host['begin']['testCwd']).iterdir())
    spec = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2346_公開値診断・null契約二追加_単体テスト仕様書.md'
    result = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2347_公開値診断・null契約二追加_製造単体結果.md'
    supplement=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2348_公開値診断・null契約二追加_仕様・完成結合追補.md'
    assert supplement.is_file()
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'code-debug.json',dict(source=SOURCE,classes=code_debug,structuralReaderVectors=selftest(),meaningProof='Independent original2 token preservation/new2 canary+seven null fields; current actual4; exact public record probe allowlist; four diagnostics no missed except naturalbranch0 NA, other Main scopes incomplete'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,tests=host['begin']['cases'],actual=dict(tests=4,suites=1,originalMethods=2,newMethods=2,newProductTestIds=2,failures=0,errors=0,skipped=0,aborted=0),newTestIds=inverse['newTestIds'],specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=[],relatedYkt=[],implementationDecision='PG-D745',codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,testClassesChanged=1,otherTestClassesUnchanged=1961,diagnosticCounters=post['diagnosticFourCounters'],diagnosticMainClasses=4,naturalDiagnosticBranchDenominatorZero=True,specificationSupplementPath=str(supplement.relative_to(data.ROOT)),specificationSupplementSha256=data.sha(supplement.read_bytes()),defaultRecordFiltersUnchanged=True,productMainExecuted=True,mainCoverageQualification='FOUR_DIAGNOSTIC_RECORDS_LINE_METHOD_CLASS_NO_MISSED_BRANCH_NA_NOT_WHOLE_ARTIFACT',wholeArtifactCoverage100=False,rawStatic=0,sourceRawCorrections=0,sourceDerivedRaw=8526,actualSecretCount=None,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
