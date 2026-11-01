"""Bind completed original denial4 proofs to their actual source, not Root authority."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17675-root-entry-denial-source-binding-v1'
RECORDS=[('PG17661-root-entry-denial-four-pt-v2','638615bb93d36af608318815228274452ca998a047ea77fe87ad3677a3d2af4c'),('PG17662-root-entry-denial-four-post-v1','733fdc388fe8048c75b75a2a386b6aadce3b071339970bf786351eae051cd508'),('PG17664-root-entry-denial-four-independent-v1','94511da038879b3527e0e3d2007da0654ca4f3cb28b9d26679778e57864508a0'),('PG17670-current2784-root-entry-denial-registry-post-v1','2ed2ca66bf71b68a81120117a1824f5c89c3edcfa7571c19fbd7e02b316d4960'),('PG17674-current2784-root-entry-denial-wbs-post-v1','d0d0e77bcba775c9483f647bf15b098e8b7812d2827e19aab543ca2e08cb47dd')]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
