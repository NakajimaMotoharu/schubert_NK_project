"""Bind passive Source supplement, with no new Product execution count."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18065-caddy-passive-source-binding-v1'
RECORDS=[["PG18050-caddy-exception-passive-post-v1","44dd5ce1b6c9d4f6eac7ab5044ee9fdff10ea292f825723625a48e3f457f6b30"],["PG18052-caddy-exception-passive-independent-v1","c78ba416730171b13c38379a61c44252acc58c2b52bb14294f6b3effbb1158a5"],["PG18059-current2863-caddy-passive-registry-v2","e3d39ba1ef37df634338d1be0bc6cb02f0104c16c3c6c634071d772288f78bba"],["PG18060-current2863-caddy-passive-registry-post-v1","3bea75de1a337f7d40c771452554e12aeb15611237b8be7df3e8c91babdf755f"],["PG18062-current2863-caddy-passive-wbs-v1","03384ebeebf0015bbedc02df01949ee964e36044daf6795ed8da9af2a87cae81"],["PG18064-current2863-caddy-passive-wbs-post-v1","03b4e18eb18754ca54787d02ffe54b2cdd488add8d630ee2f7582ea7923f944f"],["PG17882-caddy-address-boundary-six-post-v1","22f6c56e81a6194651e054694fb881c17da3857840e4db491f570d429e5851bb"],["PG17884-caddy-address-boundary-six-independent-v1","2594c867ee5d542223d53feaa3c2caaf0ab99bc378f50f1b67fbb9a9c0f9e51a"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[2][0]/'manifest.json',RECORDS[2][1])
    assert (m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'])==(2863,431,220,3018,155)
    assert (m['sourceProgramDelta'],m['measuredSourcePrograms'],m['naturalZeroBranchSourcePrograms'])==(1,597,191)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,newMeasuredExistingProductionSources=1,newProductionFiles=0,newProductTests=0,newJunitExecutions=0,newStrictFour100Sources=0,newNaturalBranchZeroSources=1,productTestsReexecutedByBinding=0,coverageExecUnion=False,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
