"""Bind independent numeric proxy boundaries and same-source whole counter replacement."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17895-caddy-address-source-binding-v1'
RECORDS=[["PG17879-caddy-address-boundary-review-v1","77f616889d01e2009827e376673b0802b93d5880e32192d416e92a2ef28d8e6b"],["PG17880-caddy-address-boundary-six-pt-v1","f4c4d89053c402a449304b947428e2f9203bc86453c90c2db39688f3094c6605"],["PG17882-caddy-address-boundary-six-post-v1","22f6c56e81a6194651e054694fb881c17da3857840e4db491f570d429e5851bb"],["PG17884-caddy-address-boundary-six-independent-v1","2594c867ee5d542223d53feaa3c2caaf0ab99bc378f50f1b67fbb9a9c0f9e51a"],["PG17888-current2833-caddy-address-registry-v1","fd5a392e2c4a2e04b354798c30fc649ed72e3943f8334750ad9067a83cb4c1a4"],["PG17890-current2833-caddy-address-registry-post-v1","43af63c82698655a7fc39ab6de11cb256c7c3f2249f7eba5db35ab26205a27d1"],["PG17892-current2833-caddy-address-wbs-v1","b2eb6cdcf37ffb143a08c15bb9c1ba10a46e32a20469116ebad24a908758a2ac"],["PG17894-current2833-caddy-address-wbs-post-v1","9115b7cf0fa92c991a925b4bb490113ac44e851e23f0719b42dd0844dfacfac8"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    name='dev/codex/schubert/nk/web/security/CaddyClientAddressResolver'
    assert m['fullSourceUnits'][name]['four100'] is True and m['qualificationReplacedUnitHistory'][name]['four100'] is False
    assert m['necessaryJointRepeatedMethods']==51 and len(m['jointQualificationReferences'])==4 and m['totalRepeatedOriginalMethods']==135
    assert m['tests']==2833 and m['totalMethodExecutions']==2968 and m['currentOrdinaryTestDeclarationReference']['existingQualityFixtureCases']==27
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,oldPartialProofPreserved=True,newFour100Sources=1,newQualityCases=6,newOrdinaryCases=0,productTestsReexecuted=0,coverageExecUnion=False,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
