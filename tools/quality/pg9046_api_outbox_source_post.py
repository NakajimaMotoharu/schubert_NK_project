"""Whole SDK-independent source plus private Entry; actual branch0 Entry is included, not excluded."""
import scoped_prometheus_post as post
import pg9044_api_outbox_source_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg9044-api-outbox-source-host-v1'
    post.RAW_SHA=post.host.sha(post.RUN/'manifest.safe.json')
    post.SLOT=post.host.W/'pg9046-api-outbox-source-post-v1'
    post.OUT=post.host.BASE/'PG9046-api-outbox-source-post-v1'
    post.MODULE='api'
    post.PREFIX='dev/codex/schubert/nk/api/monitoring/'
    names=['ApiOutboxObservationSource','ApiOutboxObservationSource$Entry']
    post.NAMES={post.PREFIX+name for name in names}
    post.CLASS_MODULES={}
    post.COMPONENT_METADATA=set()
    post.SOURCE_PATHS={'src/schubert-nk-api/src/main/java/'+post.PREFIX+name.split('$',1)[0]+'.java' for name in names}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG9044-API-OUTBOX-SOURCE'
    witness='PG9045-api-outbox-source-lock-review-v1/manifest.json'
    digest='5b5d57924ade2b358cc0f7e3d6e5457ec3dd5346fb6392691e31afb86adf4451'
    assert post.host.sha(post.host.BASE/witness)==digest
    context=__import__('json').loads((post.host.BASE/witness).read_bytes())
    assert context['source']==original.SOURCE and context['currentHostManifestSha256']==post.RAW_SHA
    post.PMD_CONTEXT=context['staticDispositions']
    post.PMD_CONTEXT_WITNESS=dict(path=witness,sha256=digest)
    assert post.SLOT.name.upper()==post.OUT.name.upper()
    post.main()
