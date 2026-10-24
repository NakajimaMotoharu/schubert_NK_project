"""Same-source new52/2 actual two context Main scopes, no native or old counter union."""
import scoped_prometheus_post as post
import pg8822_metric_refresh_fixed_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg8822-metric-refresh-fixed-host-v1'
    post.RAW_SHA='ef14dd6e0cff9a065771e0d06aa035623853a5ab5cc956c2c16e1c7624e99c33'
    post.SLOT=post.host.W/'pg8824-metric-refresh-fixed-post-v1'
    post.OUT=post.host.BASE/'PG8824-metric-refresh-fixed-post-v1'
    assert post.SLOT.name.upper()==post.OUT.name.upper()
    api='dev/codex/schubert/nk/api/monitoring/'
    web='dev/codex/schubert/nk/web/monitoring/'
    post.MODULE='web'
    post.PREFIX=web
    post.NAMES={api+'ApiMetricContext',web+'WebMetricContext',api+'ApiMetricHttpHandler',web+'WebMetricHttpHandler'}
    post.CLASS_MODULES={api+'ApiMetricContext':'api',api+'ApiMetricHttpHandler':'api',api+'package-info':'api'}
    post.COMPONENT_METADATA={api+'package-info'}
    post.SOURCE_PATHS={'src/schubert-nk-'+role+'/src/main/java/dev/codex/schubert/nk/'+role+'/monitoring/'+title+kind+'.java' for role,title in (('api','Api'),('web','Web')) for kind in ('MetricContext','MetricHttpHandler')}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG8822-METRIC-REFRESH'
    post.main()
