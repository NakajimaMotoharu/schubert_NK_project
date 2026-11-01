"""Bind five pure query catalogs; not query/DB/Graph acceptance."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18045-query-catalogs-source-binding-v1'
RECORDS=[["PG18029-query-catalogs-review-v1","d19904edea29337bfee12d1822e94791b2c3170ba1d0a2166cb97b77ca3814ad"],["PG18031-query-catalogs-five-pt-v2","6da8524044ce83418527b837e3a885b9aca3f23c3da996ce6b324138ac273498"],["PG18032-query-catalogs-five-post-v1","dddbe3c2e48becc1d44be386e444f1e3c94b4ca1ddecc0c9bd606e73b0b51e20"],["PG18034-query-catalogs-five-independent-v1","be5f38997f9fec7ba998eb9ead048a8c9e35ce0a6c7eb758477aacb70536ce78"],["PG18038-current2863-query-catalogs-registry-v1","47186edd88f768984bd9aa8d946198c2880b84b51903bd023bb6cd7f57c61fc9"],["PG18040-current2863-query-catalogs-registry-post-v1","07ce8f1563d4db10a61a74f04d58b1446f8b708a1d78bca74e02c702b4d7a685"],["PG18042-current2863-query-catalogs-wbs-v1","5946bd7432d455166d66c2213144dd8a3b2bb1a3440a49a246e49350f67fd0a6"],["PG18044-current2863-query-catalogs-wbs-post-v1","091bcdbe7d11e794b3e96077e126135c32b7dd14a436a3b3afa830d8da33eeec"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'],len(m['jointQualificationReferences']))==(2863,3018,155,71,7)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['four100SourcePrograms'],m['naturalZeroBranchSourcePrograms'],m['incompleteSourcePrograms'])==(5,596,303,190,80)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=5,newProductionFiles=0,newFour100Sources=4,newThreeCounter100NaturalBranchZeroSources=1,newQualityCases=5,newOrdinaryCases=0,originalRepeatedCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualQueryOrSqlstateClassification=False,actualThrowableGraphTraversal=False,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
