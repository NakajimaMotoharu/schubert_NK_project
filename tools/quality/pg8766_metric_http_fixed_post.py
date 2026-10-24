"""Same-source new52/2 actual two context Main scopes, no native or old counter union."""
import scoped_prometheus_post as post
import pg8764_metric_http_fixed_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg8764-metric-http-fixed-host-v1'
    post.RAW_SHA='5e39866ccbc772919a8c4beac4e8cb1a3e6add69135f60419663efb5b786304d'
    post.SLOT=post.host.W/'pg8766-metric-http-fixed-post-v1'
    post.OUT=post.host.BASE/'PG8766-metric-http-fixed-post-v1'
    assert post.SLOT.name.upper()==post.OUT.name.upper()
    api='dev/codex/schubert/nk/api/monitoring/'
    web='dev/codex/schubert/nk/web/monitoring/'
    post.MODULE='web'
    post.PREFIX=web
    post.NAMES={api+'ApiMetricHttpHandler',web+'WebMetricHttpHandler'}
    post.CLASS_MODULES={api+'ApiMetricHttpHandler':'api',api+'package-info':'api'}
    post.COMPONENT_METADATA={api+'package-info'}
    post.SOURCE_PATHS={'src/schubert-nk-'+role+'/src/main/java/dev/codex/schubert/nk/'+role+'/monitoring/'+title+'MetricHttpHandler.java' for role,title in (('api','Api'),('web','Web'))}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG8764-METRIC-HTTP'
    post.main()
