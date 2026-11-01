"""Bind complete pure auth values/catalog Sources; no actual authentication or session issuance."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18105-auth-values-source-binding-v1'
RECORDS=[["PG18089-auth-values-review-v1","1c4e341150b77a63ea9dee3ed6ee0fc024f5b761ed3c6d8c8e5377e181c7c17c"],["PG18090-auth-values-twelve-pt-v1","f55a5c6f9f5d54619d17f7379923a8554d830396939f2ae61b3a831a78b3cac4"],["PG18092-auth-values-twelve-post-v1","60181f567c9bda57f67b07a482bc3064aa4f5d4562fea2065a7d1e05f21e3576"],["PG18094-auth-values-twelve-independent-v1","2dc54a83979736b3aad534c85914fa709103681d9366a11cc73c6504baf62e91"],["PG18098-current2883-auth-values-registry-v1","6435d0129082e022ea83152bcf8cf25ff350290b724ba885ad1df22cf5938a12"],["PG18100-current2883-auth-values-registry-post-v1","2b0e1f6d7e3e544248e3486736c9d1da80b631dbc4a092e9723592bbf1a979b1"],["PG18102-current2883-auth-values-wbs-v1","f1a6966eb1a915348a3c4fecdbfccb04073528fe8b8bb0a15320c012d9641ad4"],["PG18104-current2883-auth-values-wbs-post-v1","d133049f62433ff8956406b7dcb013d8af09a567a34bddf8ccf0a834194056d0"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2883,433,222,3038,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['executablePhysical'],m['metadataPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(9,610,1047,848,199,312,461,195,212)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=9,newProductionFiles=0,newFour100Sources=5,newNaturalBranchZeroThreeCounterSources=4,newAbstractNoCodePhysicalClasses=1,newQualityCases=12,newOrdinaryCases=0,originalRepeatedCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualAuthenticationOrSessionIssued=False,actualKeyOrCryptoOperations=False,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
