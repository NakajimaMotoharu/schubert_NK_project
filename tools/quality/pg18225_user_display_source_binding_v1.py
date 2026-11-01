"""Bind two User display Sources and corrected independent oracle; no actual auth/DB acceptance."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18225-user-display-source-binding-v1'
RECORDS=[["PG18209-user-display-review-v1","08defa860ba51afcd5d919de9067fc45e586f5f9194743652cdc167e1db1ace3"],["PG18210-user-display-eight-pt-v1","7bc53799010fd5d23a4e35c665c604407f7144f9288f76c021f4fd14cbf9cabe"],["PG18212-user-display-eight-post-v1","1ae44fb4997505174d3b36cc7058b67bf5876c8929a8ac56d7f84d166c298445"],["PG18214-user-display-eight-independent-v1","f05e5f657ed1306e469629a130c3c74cf50c2301e5818a2938b6fd7af9feadb6"],["PG18218-current2925-user-display-registry-v1","d13f433b3f6d15e9bc44ac9fc88aeb0113b82847dbbd5d2781be47aef4baedb9"],["PG18220-current2925-user-display-registry-post-v1","58d3401061d77f8bf3afa48a2af5c85629316f54410028e695dac5611c2b1906"],["PG18222-current2925-user-display-wbs-v1","3c627b63acfa486c81bfbb396e077756c7b5c04e8629a1f5cc96ba9e1e45833a"],["PG18224-current2925-user-display-wbs-post-v1","227b5df169214d08699ccb99c7624fc4d112d387420238af95368fc9e14ed3ab"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2925,439,228,3080,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(2,629,1069,326,477,200,218)
    q=data.read_checked(data.BASE/RECORDS[3][0]/'manifest.json',RECORDS[3][1]);assert q['independentUnicodeBasisNegativeVectors']==2 and q['correctedSpecificationSha256']=='e15ca367ce07647acc8675867170e15225a8d3917db7a3963018fad842d9cbb6'
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=2,newProductionFiles=0,newFour100Sources=2,newNaturalBranchZeroThreeCounterSources=0,newQualityCases=8,newOrdinaryCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,localDisplayRoleGuardExecuted=True,actualExternalAuthorizationOrMutation=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
