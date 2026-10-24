"""Full one-Main RO owner actual coverage/static/CRC/current XML; real DB/worker/native unqualified."""
import json
import scoped_prometheus_post as post
import pg9156_api_observation_context_host_v5 as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg9156-api-observation-context-host-v4'
    post.RAW_SHA=post.host.sha(post.RUN/'manifest.safe.json')
    post.SLOT=post.host.W/'pg9158-api-observation-context-post-v1'
    post.OUT=post.host.BASE/'PG9158-api-observation-context-post-v1'
    post.MODULE='api'
    post.PREFIX='dev/codex/schubert/nk/api/monitoring/'
    post.NAMES={post.PREFIX+'ApiObservationContext'}
    post.CLASS_MODULES={}
    post.COMPONENT_METADATA=set()
    post.SOURCE_PATHS={'src/schubert-nk-api/src/main/java/'+post.PREFIX+'ApiObservationContext.java'}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG9156-API-OBSERVATION-CONTEXT-V4'
    witness='PG9157-api-observation-context-review-v1/manifest.json'
    digest='a728b7c177342e3d6f9931daa0b1b8bd3d2fcdf10bc8c2977c7bb33014e17eb6'
    assert post.host.sha(post.host.BASE/witness)==digest
    context=json.loads((post.host.BASE/witness).read_bytes())
    assert context['source']==original.SOURCE and context['currentHostManifestSha256']==post.RAW_SHA
    post.PMD_CONTEXT=context['staticDispositions']
    post.PMD_CONTEXT_WITNESS=dict(path=witness,sha256=digest)
    assert len(post.PMD_CONTEXT)==4 and post.SLOT.name.upper()==post.OUT.name.upper()
    post.main()
