"""Full one-Main RO owner actual coverage/static/CRC/current XML; real DB/worker/native unqualified."""
import json
import scoped_prometheus_post as post
import pg9082_api_ro_attempt_typed_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg9082-api-ro-attempt-typed-host-v1'
    post.RAW_SHA=post.host.sha(post.RUN/'manifest.safe.json')
    post.SLOT=post.host.W/'pg9084-api-ro-attempt-typed-post-v1'
    post.OUT=post.host.BASE/'PG9084-api-ro-attempt-typed-post-v1'
    post.MODULE='api'
    post.PREFIX='dev/codex/schubert/nk/api/monitoring/'
    post.NAMES={post.PREFIX+'ApiReadOnlyObservationAttempt'}
    post.CLASS_MODULES={}
    post.COMPONENT_METADATA=set()
    post.SOURCE_PATHS={'src/schubert-nk-api/src/main/java/'+post.PREFIX+'ApiReadOnlyObservationAttempt.java'}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG9082-API-RO-ATTEMPT-TYPED'
    witness='PG9085-api-ro-attempt-context-v1/manifest.json'
    digest='REVIEW_PENDING'
    assert post.host.sha(post.host.BASE/witness)==digest
    context=json.loads((post.host.BASE/witness).read_bytes())
    assert context['source']==original.SOURCE and context['currentHostManifestSha256']==post.RAW_SHA
    post.PMD_CONTEXT=context['staticDispositions']
    post.PMD_CONTEXT_WITNESS=dict(path=witness,sha256=digest)
    assert len(post.PMD_CONTEXT)==12 and post.SLOT.name.upper()==post.OUT.name.upper()
    post.main()
