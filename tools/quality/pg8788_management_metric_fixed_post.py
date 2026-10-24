"""Same-source new52/2 actual two context Main scopes, no native or old counter union."""
import scoped_prometheus_post as post
import pg8786_management_metric_fixed_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg8786-management-metric-fixed-host-v1'
    post.RAW_SHA='48456d325d6acef25370360c544549bb171a412878dfb03f8363185780f22339'
    post.SLOT=post.host.W/'pg8788-management-metric-fixed-post-v1'
    post.OUT=post.host.BASE/'PG8788-management-metric-fixed-post-v1'
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
    post.EXPECTED_SESSION='PG8786-MANAGEMENT-METRIC'
    post.main()
