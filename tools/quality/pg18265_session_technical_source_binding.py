"""Bind exact technical row/fixed exception evidence, not service authentication or commit."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18265-session-technical-source-binding-v1'
RECORDS=[["PG18249-session-technical-review-v1","aa604b5d10e93e9aee5d2fca9abb14e3377b7c70ec754794036e48836c237038"],["PG18250-session-technical-eight-pt-v1","3f9bc0ebc922fc0a078d807e16f4538a41587536c7796779ef6796d90d74d856"],["PG18252-session-technical-eight-post-v1","c0e7c808620062b432092d00eb1eeddeac3c918dc5b0593ac6cc6b136858aa71"],["PG18254-session-technical-eight-independent-v1","944ca3cc17044ca459de623d2def614deaca84eef5ca1c12b9ce6e464ca5a43b"],["PG18258-current2945-session-technical-registry-v1","b1d06d3872fbf6e666b494cf5324932164294e1b809f6802f3f558f32a8954fd"],["PG18260-current2945-session-technical-registry-post-v1","693818764bdd6b7d6981cca2cb0be5d4bdc9a0c13485b629bd0e67b209bb5073"],["PG18262-current2945-session-technical-wbs-v1","0f411b9fd95b68e9d49a432ccef7e135d903d54262b76a85868c9819dfa75d01"],["PG18264-current2945-session-technical-wbs-post-v1","84f1e8507fa54385e7fe1fb758bd498e7854d442c26e0b5a1ca40b63d3042510"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'])==(2945,441,230,3100,155,71)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'])==(4,635,1076,329,481,203,221)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=4,newProductionFiles=0,newFour100Sources=1,newNaturalBranchZeroThreeCounterSources=3,newQualityCases=8,newOrdinaryCases=0,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualAuthenticationOrSessionIssued=False,actualJmsIsolationOrCommitInvoked=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
