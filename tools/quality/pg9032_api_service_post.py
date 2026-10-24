"""Current binding/HTTP two Main actual four100/static; no caller or live-source qualification."""
import scoped_prometheus_post as post
import pg9030_api_service_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg9030-api-service-host-v1'
    post.RAW_SHA=post.host.sha(post.RUN/'manifest.safe.json')
    post.SLOT=post.host.W/'pg9032-api-service-post-v1'
    post.OUT=post.host.BASE/'PG9032-api-service-post-v1'
    post.MODULE='api'
    post.PREFIX='dev/codex/schubert/nk/api/monitoring/'
    names=['ApiServiceMetricBinding','ApiMetricHttpHandler']
    post.NAMES={post.PREFIX+name for name in names}
    post.CLASS_MODULES={}
    post.COMPONENT_METADATA=set()
    post.SOURCE_PATHS={'src/schubert-nk-api/src/main/java/'+post.PREFIX+name+'.java' for name in names}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG9030-API-SERVICE'
    post.PMD_CONTEXT=()
    post.PMD_CONTEXT_WITNESS=None
    assert post.SLOT.name.upper()==post.OUT.name.upper()
    post.main()
