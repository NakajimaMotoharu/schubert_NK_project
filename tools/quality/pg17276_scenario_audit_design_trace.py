"""Scenario audit-specific approved trace and exact JUnit identities; no execution or source mutation."""
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17276-scenario-audit-design-trace-v1'
INDEPENDENT=('PG17275-scenario-audit-five-independent-v2','856d7ceb545215bdabcb8758fd36bd9865c739863b37753da69ccd32aec633f7')
POST=('PG17272-scenario-audit-five-post-v1','d8cc4985b0290ff4e83ae1219ba953b261b9049e99549f167fd11543a9df1874')
METHODS=['searchCountAndSensitiveConditionsNeverLeak','inlineAndFileUseTheirIndependentRecordCounts','nonCatalogListQueriesDoNotTouchDatabase','sqlFailuresArePropagatedWithStatementOwnership','nullBoundaryFailsBeforeDatabaseEffects']
def main():
    invocation=capture(__file__);assert not OUT.exists()
    q,p=[data.read_checked(data.BASE/name/'manifest.json',pin) for name,pin in [INDEPENDENT,POST]]
    assert all(v['actualExit']==0 and v['source']==SOURCE and v['tests']==5 for v in [q,p]) and q['postSha256']==POST[1] and q['independentOracleVectors']==5
    refs={}
    for root,nums in [('documents/300_SS',['323','324','332','351','352']),('documents/200_UI',['234','237']),('documents/100_RD',['121','171'])]:
        for num in nums:
            paths=list((data.ROOT/root).glob('*/'+num+'_*.md'));assert len(paths)==1
            path=paths[0];relative=str(path.relative_to(data.ROOT));blob=path.read_bytes()
            assert blob==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT);refs[relative]=data.sha(blob)
    prefix='src/schubert-nk-api/src/'
    main_path=prefix+'main/java/dev/codex/schubert/nk/api/application/scenario/ScenarioAuditWriter.java'
    test_path=prefix+'test/java/dev/codex/schubert/nk/api/application/scenario/ScenarioAuditWriterTest.java'
    fixture_path=prefix+'test/java/dev/codex/schubert/nk/api/application/scenario/ScenarioRequestFixture.java'
    text=(data.ROOT/main_path).read_text()
    assert text.count('Objects.requireNonNull(')==5 and 'catch (NullPointerException' not in text
    assert all(v in text for v in ['NK-SCN-001','FUN003..005/MON003004','UI234237','SS323324332351352','SCENARIO_SEARCHED','SCENARIO_VIEWED'])
    cases={v['name']:v for v in p['cases']};assert set(cases)==set(METHODS)
    mapping=[dict(testId='dev.codex.schubert.nk.api.application.scenario.ScenarioAuditWriterTest#'+n,className=cases[n]['classname'],method=n,actualResult=cases[n]['result'],legacyRangeImplicitlyZipped=False) for n in METHODS]
    rd_text=(next((data.ROOT/'documents/100_RD').glob('*/171_*.md'))).read_text()
    assert all(v in rd_text for v in ['MON-003','MON-004','session token'])
    ss_text=(next((data.ROOT/'documents/300_SS').glob('*/351_*.md'))).read_text()
    assert all(v in ss_text for v in ['SCENARIO_SEARCHED','SCENARIO_VIEWED','keyword/bodyなし','DB監査が正本'])
    verify(q['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,originalIndependentPost=list(INDEPENDENT),originalPost=list(POST),approvedDesignHashes=refs,originMain=subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip(),programId='NK-SCN-001',className='dev.codex.schubert.nk.api.application.scenario.ScenarioAuditWriter',method='write',sourcePath=main_path,sourceSha256=data.sha(text.encode()),testSourcePath=test_path,testSourceSha256=data.sha((data.ROOT/test_path).read_bytes()),originalFixturePath=fixture_path,originalFixtureSha256=data.sha((data.ROOT/fixture_path).read_bytes()),caseMappings=mapping,directRequirementIds=['MON-003','MON-004'],supportingBusinessIds=['FUN-003','FUN-004'],indirectNotQualifiedRequirementIds=['FUN-005'],sourceLegacyTestRange='PT-SCN-AUD469001..008',testLegacyRange='PT-SCN-AUD469003..006',implicitLegacyIdMethodZip=False,wholeInboxReplayTransactionRealDatabaseOrAudioQualified=False,originalGenericReferencesRetained=True,sourceChanged=False,designChanged=False,productTestsExecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None)
    data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
