"""Full one-Main RO owner actual coverage/static/CRC/current XML; real DB/worker/native unqualified."""
import json
import scoped_prometheus_post as post
import pg9120_api_outbox_pump_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg9120-api-outbox-pump-host-v1'
    post.RAW_SHA=post.host.sha(post.RUN/'manifest.safe.json')
    post.SLOT=post.host.W/'pg9122-api-outbox-pump-post-v1'
    post.OUT=post.host.BASE/'PG9122-api-outbox-pump-post-v1'
    post.MODULE='api'
    post.PREFIX='dev/codex/schubert/nk/api/monitoring/'
    post.NAMES={post.PREFIX+'ApiOutboxObservationPump'}
    post.CLASS_MODULES={}
    post.COMPONENT_METADATA=set()
    post.SOURCE_PATHS={'src/schubert-nk-api/src/main/java/'+post.PREFIX+'ApiOutboxObservationPump.java'}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG9120-API-OUTBOX-PUMP'
    witness='PG9121-api-outbox-pump-context-v1/manifest.json'
    digest='2a65576e7ac6ff097fa0010e05a5ec08c6afe15b601b9b6abdf0da23bd93db20'
    assert post.host.sha(post.host.BASE/witness)==digest
    context=json.loads((post.host.BASE/witness).read_bytes())
    assert context['source']==original.SOURCE and context['currentHostManifestSha256']==post.RAW_SHA
    post.PMD_CONTEXT=context['staticDispositions']
    post.PMD_CONTEXT_WITNESS=dict(path=witness,sha256=digest)
    assert len(post.PMD_CONTEXT)==3 and post.SLOT.name.upper()==post.OUT.name.upper()
    post.main()
