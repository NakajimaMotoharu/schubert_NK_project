"""Bind request-display evidence without accepting HTTP/session/DB/business paths."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18205-request-display-source-binding-v1'
RECORDS=[["PG18189-request-display-review-v1","71dfcc3084c1776d4a81aa48999bc6198782b9322b666724a4e0b0ead71c3810"],["PG18190-request-display-ten-pt-v1","be260ea2a4ad517e319a1bbbb8c90055ec7483354176fa20269a057ad041aed5"],["PG18192-request-display-ten-post-v1","f9552f487cb87e12be3fd1586e0383af19615fb1ee10673b860b8cf5bc6cb027"],["PG18194-request-display-ten-independent-v1","bb07b86290e2ccb0948f340f5990f3bb8f0a2931193099505884321ea33e1436"],["PG18198-current2917-request-display-registry-v1","6551658fcc9bad07e701e3eb28bfbdbd51d660dd9606b17d6e28ba5e8a163054"],["PG18200-current2917-request-display-registry-post-v1","5fb3016c181d8a85f31b29a0aed6b69e5404bf818ac74897e3c5ea04a5a0a19b"],["PG18202-current2917-request-display-wbs-v1","2c191f1710b31d3df6ea700981767511e095465cd6cd41a546be51562f63a1d3"],["PG18204-current2917-request-display-wbs-post-v1","6e870db502b76cc7f9704c2adb5190b56a284f67c7d7d92c1f78af07952c48e7"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2917,438,227,3072,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(4,627,1066,324,474,200,218)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=4,newProductionFiles=0,newFour100Sources=4,newNaturalBranchZeroThreeCounterSources=0,newQualityCases=10,newOrdinaryCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualHttpAuthenticationBusinessOrDbCertified=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
