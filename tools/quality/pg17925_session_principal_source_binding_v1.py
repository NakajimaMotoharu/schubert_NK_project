"""Bind same-source principal snapshot invariants and fixed predecessor/OUT namespace."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17925-session-principal-source-binding-v1'
RECORDS=[["PG17909-session-principal-boundary-review-v1","9ab220a7480bfe027d3229da85e384e8b6857c8b5a49a7f07559de7ff3df7031"],["PG17910-session-principal-boundary-five-pt-v1","10e447a191229f8a74566e03259e828a729644c9b3cf1c26b4fd2521efd000d2"],["PG17912-session-principal-boundary-five-post-v1","d560235918b9a547adbd511a74563a3b8d5388dbe9ba337a65fb2891ebf60676"],["PG17914-session-principal-boundary-five-independent-v1","903cf55c01aec31640f320030ec46ccbd5ba7a860b5eb2cb9355e5a9b6257984"],["PG17919-current2838-session-principal-registry-v2","ac992c8e92288235c219c8331a7801a36084b8e6387d5949945552515de5ee27"],["PG17920-current2838-session-principal-registry-post-v1","9f4976670cd75b0fb07019c932b62d7646ce062054551c1486025e9d8efa4597"],["PG17922-current2838-session-principal-wbs-v1","45bc4f20e8c7992a71ff8416b27ebe85ff58041c294686c321f2c8458f6e3356"],["PG17924-current2838-session-principal-wbs-post-v1","41848e6a9324d321912dd866f840aa7a2c291e64b6339805c55b54f9006629b3"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1]);q=data.read_checked(data.BASE/RECORDS[5][0]/'manifest.json',RECORDS[5][1])
    name='dev/codex/schubert/nk/web/session/SessionPrincipal'
    assert m['fullSourceUnits'][name]['four100'] is True and m['qualificationReplacedUnitHistory'][name]['four100'] is False
    assert m['necessaryJointRepeatedMethods']==51 and len(m['jointQualificationReferences'])==4 and m['totalRepeatedOriginalMethods']==135
    assert m['tests']==2838 and m['totalMethodExecutions']==2973 and m['currentOrdinaryTestDeclarationReference']['existingQualityFixtureCases']==32
    assert m['registryInputNegativeVectors']==q['registryInputNegativeVectors']==2
    failed=data.ROOT/'tools/quality/pg17918_current2838_session_principal_registry_v1.py'
    assert data.sha(failed.read_bytes())=='2def97e657f3c4765ae0e0fe2834b439d8ae68fda5571e934e889efa71640333'
    assert not (data.BASE/'PG17918-current2838-session-principal-registry-v1').exists()
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,failedRegistryEntrySha256=data.sha(failed.read_bytes()),failedRegistryOriginalExit=1,failedRegistryOutputNotCreated=True,inputOutputProfileNegativeVectors=2,oldPartialProofPreserved=True,newFour100Sources=1,newQualityCases=5,newOrdinaryCases=0,productTestsReexecuted=0,coverageExecUnion=False,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
