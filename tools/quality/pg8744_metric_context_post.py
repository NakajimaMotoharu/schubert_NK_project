"""Same-source new52/2 actual two context Main scopes, no native or old counter union."""
import scoped_prometheus_post as post
import pg8742_metric_context_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg8742-metric-context-host-v1'
    post.RAW_SHA='5510543f8acc66b6fc64c3dfeced5bc89a4324b7fd3ad0b36e5261eb7df245a0'
    post.SLOT=post.host.W/'pg8744-metric-context-post-v1'
    post.OUT=post.host.BASE/'PG8744-metric-context-post-v1'
    assert post.SLOT.name.upper()==post.OUT.name.upper()
    api='dev/codex/schubert/nk/api/monitoring/'
    web='dev/codex/schubert/nk/web/monitoring/'
    post.MODULE='web'
    post.PREFIX=web
    post.NAMES={api+'ApiMetricContext',web+'WebMetricContext'}
    post.CLASS_MODULES={api+'ApiMetricContext':'api',api+'package-info':'api'}
    post.COMPONENT_METADATA={api+'package-info'}
    post.SOURCE_PATHS={'src/schubert-nk-'+role+'/src/main/java/dev/codex/schubert/nk/'+role+'/monitoring/'+title+'MetricContext.java' for role,title in (('api','Api'),('web','Web'))}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG8742-METRIC-CONTEXT'
    post.main()
