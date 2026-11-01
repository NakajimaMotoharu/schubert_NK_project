"""Bind current successful public-provider proofs, never actual native qualification."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17635-checkpoint-public-provider-source-binding-v1'
RECORDS=[('PG17620-checkpoint-public-provider-twelve-pt-v1','2b1c9fe2b25c4f058b64649c2b15dd916d7ca92f9370fe73b86ce3a6ce5b45b9'),('PG17622-checkpoint-public-provider-twelve-post-v1','763b612944c5e1559664c5ff6d99ec9b3de81459a30c4bb3c0036f2091645745'),('PG17624-checkpoint-public-provider-twelve-independent-v1','d66682cd4fe2478d07a079f6eac53b485bd6578d667763b4960b4b2dec6dea3d'),('PG17630-current2774-checkpoint-public-provider-registry-post-v1','499cb96aed7d848ae9c40d8933b241c51b8b50bdfa54cd503ad1b500fd99c07d'),('PG17634-current2774-checkpoint-public-provider-wbs-post-v1','65f7b88549e22a620487a891ca2ec97cd7b9ea8faa7399ec5009484c32f60706')]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,productTestsReexecuted=0,actualNativeQualificationClaimed=False,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
