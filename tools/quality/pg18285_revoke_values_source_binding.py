"""Bind exact revocation projection evidence; no claim/send/credential operation."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18285-revoke-values-source-binding-v1'
RECORDS=[["PG18269-revoke-values-review-v1","06b3985a4f40b14e8adccfdde6c3a648b088c5803448fbf8717f5916265201fa"],["PG18270-revoke-values-ten-pt-v1","f6ed226b28aec2caa4a2e98eb6ad15ca04a9ceeecd4677f58952ee5c509621f7"],["PG18272-revoke-values-ten-post-v1","59d3ca7c5ec71ddf3838ee579816012a643eb26939761f74ff16158bd4f568fd"],["PG18274-revoke-values-ten-independent-v1","186f8a2fb345ce3fffc0ebe12c33f273cfcee9d795c931a630975ec63a6ab63c"],["PG18278-current2955-revoke-values-registry-v1","1f8ddb95b0f15c064e702f6ace5023309575a4ddb3796bdb4c8fec1cda26ade3"],["PG18280-current2955-revoke-values-registry-post-v1","3a1b0bde1131fe01db59eaaf82dbb6e02a87cf95b6b5df5da0e60629f688b78b"],["PG18282-current2955-revoke-values-wbs-v1","ba95270992808d4a55f04af84c14e616318e72ec0fe7d5a1670cb9687db17c4a"],["PG18284-current2955-revoke-values-wbs-post-v1","c6466f87f3fabd7bea2b0c1948eeddd306aa1c599f38b2c1b3a6cca82c45ede4"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2955,442,231,3110,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(6,641,1082,330,482,208,226)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=6,newProductionFiles=0,newFour100Sources=1,newNaturalBranchZeroThreeCounterSources=5,newQualityCases=10,newOrdinaryCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualClaimOrRetryInvoked=False,actualJmsIsolationOrCommitInvoked=False,actualCredentialFileRead=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
