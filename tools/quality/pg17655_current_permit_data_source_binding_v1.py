"""Bind actual six-case scope/source proofs; no real permit/Root authority."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17655-current-permit-data-source-binding-v1'
RECORDS=[('PG17641-current-permit-data-six-pt-v2','48db9be724e1cd42954cd54e9fd48367ed199bb472490df14f253041c3b98a53'),('PG17642-current-permit-data-six-post-v1','f59b1db5c4b23ed3981bad802ab621b9f90dce497ac030ce73d4a7892b87cfea'),('PG17644-current-permit-data-six-independent-v1','d59a5f733907ca5badb4b3805a338f89209f2bfbea4f01d9c584d2af68bc840e'),('PG17650-current2780-permit-data-registry-post-v1','ce166c4d8b591dbd8b29c0345e8fce5d0b4a2ee1b2e90f1d19dfb2aeebaeab68'),('PG17654-current2780-permit-data-wbs-post-v1','ad180c5a0c124f78ee03ab69a9559f7582327bcb7a853be3b35e099b014bbdb5')]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,productTestsReexecuted=0,actualPermitOrRootQualificationClaimed=False,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
