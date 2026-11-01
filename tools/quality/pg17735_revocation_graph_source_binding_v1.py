"""Bind independent original revocation graph3 same-source evidence, no actual revocation authority."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17735-revocation-graph-source-binding-v1'
RECORDS=[('PG17720-revocation-graph-three-pt-v1','918c173e5540676e824c1fe2855bcaf433753c942e3f94c410eb175d4c0b0b68'),('PG17722-revocation-graph-three-post-v1','0281f99d232137b79e2adff27f4e340fc7236d27ce8283d484fe4dd47046c268'),('PG17725-revocation-graph-three-independent-v2','77f32b2bb28610706ec52ae2a8f5b689006eb65368733e0864cbc94a34bd368b'),('PG17730-current2804-revocation-graph-registry-post-v1','484b1d0fc7f932e2ff773eac6c616b6df743f4d0e91a5414e521b9de8c6bcc53'),('PG17734-current2804-revocation-graph-wbs-post-v1','a318d3bb00a104b29ec20e32120bf87ddef110ce1c2f9b89c5afbd2f2932b953')]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
