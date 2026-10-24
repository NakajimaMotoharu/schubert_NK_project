"""Current new service binding plus unchanged HTTP consumer, exact scope2 four counters/static."""
import scoped_prometheus_post as post
import pg8934_web_service_metric_fixed_host as original
if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg8934-web-service-metric-fixed-host-v1'
    post.RAW_SHA=post.host.sha(post.RUN/'manifest.safe.json')
    post.SLOT=post.host.W/'pg8936-web-service-metric-fixed-post-v1'
    post.OUT=post.host.BASE/'PG8936-web-service-metric-fixed-post-v1'
    post.MODULE='web'
    post.PREFIX='dev/codex/schubert/nk/web/monitoring/'
    post.NAMES={post.PREFIX+name for name in ('WebServiceMetricBinding','WebMetricHttpHandler')}
    post.CLASS_MODULES={}
    post.COMPONENT_METADATA=set()
    post.SOURCE_PATHS={'src/schubert-nk-web/src/main/java/'+name+'.java' for name in post.NAMES}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG8934-WEB-SERVICE-METRIC'
    post.PMD_CONTEXT=[]
    assert post.SLOT.name.upper()==post.OUT.name.upper()
    post.main()
