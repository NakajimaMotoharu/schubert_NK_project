"""Whole SDK-independent source plus private Entry; actual branch0 Entry is included, not excluded."""
import scoped_prometheus_post as post
import pg9106_api_cleanup_publication_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg9106-api-cleanup-publication-host-v1'
    post.RAW_SHA=post.host.sha(post.RUN/'manifest.safe.json')
    post.SLOT=post.host.W/'pg9108-api-cleanup-publication-post-v1'
    post.OUT=post.host.BASE/'PG9108-api-cleanup-publication-post-v1'
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
    post.EXPECTED_SESSION='PG9106-API-CLEANUP-PUBLICATION'
    witness='PG9107-api-cleanup-publication-lock-review-v1/manifest.json'
    digest='2f475ac30e7d04d24079ee464fa4c009b7a01e95537727598204239a633b76f2'
    assert post.host.sha(post.host.BASE/witness)==digest
    context=__import__('json').loads((post.host.BASE/witness).read_bytes())
    assert context['source']==original.SOURCE and context['currentHostManifestSha256']==post.RAW_SHA
    post.PMD_CONTEXT=context['staticDispositions']
    post.PMD_CONTEXT_WITNESS=dict(path=witness,sha256=digest)
    assert post.SLOT.name.upper()==post.OUT.name.upper()
    post.main()
