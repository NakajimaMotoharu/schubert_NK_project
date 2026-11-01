"""Bind pure readiness new-two and necessary-repeat-four without transferring older exec coverage."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17945-web-ready-source-binding-v1'
RECORDS=[["PG17929-web-ready-pure-review-v1","b72e0dd8cb5232e299650f26a8b3e85329cfa2f74d222a478cf67773dca644ac"],["PG17930-web-ready-pure-six-pt-v1","de1da3da5048d74974cc7b15bf58b5cd8c96401591ad6bfaa5cf8330ec0f933c"],["PG17932-web-ready-pure-six-post-v1","6fdab1613acdc4d08545da6b00e72bda759e8f1b1f53f1786767df05e3fed0d7"],["PG17934-web-ready-pure-six-independent-v1","5802689466c1c60ed2ebd136664969ebda2f543ce288eec304c2a78bbc3fbe7f"],["PG17938-current2840-web-ready-joint-registry-v1","a1289d9a32aa20e1c70eb06cf309b655f77f0af8150e13bd4b93ab3be84e2c06"],["PG17940-current2840-web-ready-joint-registry-post-v1","52b90797d0975f8ddd31ffb5630d1ec49d9d9d093024908d90054c8c39527dca"],["PG17942-current2840-web-ready-joint-wbs-v1","dd066f6462e389568040b4d775b6456f92c4cb46815aa2f59a4c4448f5e044ed"],["PG17944-current2840-web-ready-joint-wbs-post-v1","df71d2ec343d1ab016d601aaa82ff85bca3bd2ce90254354684b7e887e7e8c53"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    name='dev/codex/schubert/nk/web/bootstrap/WebRuntimeHealth'
    assert m['fullSourceUnits'][name]['four100'] is True and m['jointQualificationReplacedUnitHistory'][name]['four100'] is False
    assert m['necessaryJointRepeatedMethods']==55 and len(m['jointQualificationReferences'])==5 and m['totalRepeatedOriginalMethods']==139
    assert m['tests']==2840 and m['totalMethodExecutions']==2979 and m['currentOrdinaryTestDeclarationReference']['existingQualityFixtureCases']==34
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,oldPartialProofPreserved=True,newFour100Sources=1,newQualityCases=2,necessaryOriginalRepeatedCases=4,newOrdinaryCases=0,productTestsReexecuted=0,coverageExecUnion=False,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
