"""Full one-Main RO owner actual coverage/static/CRC/current XML; real DB/worker/native unqualified."""
import json
import scoped_prometheus_post as post
import pg9134_api_observation_worker_host_v2 as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg9134-api-observation-worker-host-v2'
    post.RAW_SHA=post.host.sha(post.RUN/'manifest.safe.json')
    post.SLOT=post.host.W/'pg9136-api-observation-worker-post-v1'
    post.OUT=post.host.BASE/'PG9136-api-observation-worker-post-v1'
    post.MODULE='api'
    post.PREFIX='dev/codex/schubert/nk/api/monitoring/'
    post.NAMES={post.PREFIX+'OwnedApiObservationWorker'}
    post.CLASS_MODULES={}
    post.COMPONENT_METADATA=set()
    post.SOURCE_PATHS={'src/schubert-nk-api/src/main/java/'+post.PREFIX+'OwnedApiObservationWorker.java'}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG9134-API-OBSERVATION-WORKER-V2'
    witness='PG9135-api-observation-worker-context-v1/manifest.json'
    digest='c1be834044f886aaf6f92ce619da09f1e9a3c00923afa8cd387b105b3415b44b'
    assert post.host.sha(post.host.BASE/witness)==digest
    context=json.loads((post.host.BASE/witness).read_bytes())
    assert context['source']==original.SOURCE and context['currentHostManifestSha256']==post.RAW_SHA
    post.PMD_CONTEXT=context['staticDispositions']
    post.PMD_CONTEXT_WITNESS=dict(path=witness,sha256=digest)
    assert len(post.PMD_CONTEXT)==20 and post.SLOT.name.upper()==post.OUT.name.upper()
    post.main()
