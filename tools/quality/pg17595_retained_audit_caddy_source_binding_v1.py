"""Bind five actual source/run proofs without original-test replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17595-retained-audit-caddy-source-binding-v1'
RECORDS=[["PG17580-retained-audit-caddy-fifteen-pt-v1","53f590aa8e3877d3b918b6344043e3edb9598ff47071694e7025d7ed38877222"],["PG17582-retained-audit-caddy-fifteen-post-v1","6f43a60465ff60cf9e35bf70cc6fc6b53760c0b738f51f5fe57300ffd8699c01"],["PG17584-retained-audit-caddy-fifteen-independent-v1","00e911622cf70094d9bd9f8b48bd8b4eac9f0b96c8792b8ced319458c49b4d33"],["PG17590-current2762-retained-audit-caddy-registry-post-v1","714b45069be9c46997757a14af0b6cabfc3cdf6162ba9b07bed0cabdb7476007"],["PG17594-current2762-retained-audit-caddy-wbs-post-v1","ae8533a4349e98ec6e955c0d8619beab481f1732fef9d9fb226281bb17b11b14"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
