"""Bind same-source graph8 and closed disclosure correction, never transfer another source/run."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17715-session-auth-graph-source-binding-v1'
RECORDS=[('PG17700-session-auth-graph-eight-pt-v1','dd8b3d2e64f3b3ab05072d84e878ed968dfc42bf30e2021550835da2567513e8'),('PG17703-session-auth-graph-disclosure-post-v2','9edb754483f74fb5f665cb314a346b4f5f6932240ea1a8b7392d1a1112aea10c'),('PG17705-session-auth-graph-disclosure-independent-v2','0bfc39ede2a488d821eddc91fa8187d5a07fc557c46e7607a7453354543a7556'),('PG17710-current2801-session-auth-graph-registry-post-v1','6b365fbc7cacda2e581b58648bc0d40fece6fe6bef3a5bce49e102e6416cf6a9'),('PG17714-current2801-session-auth-graph-wbs-post-v1','28bfde2616a19f94c4b18c3941f0d6109a67045cb57918ed0d9f60b3c2bd4501')]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
