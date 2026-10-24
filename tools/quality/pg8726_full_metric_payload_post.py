"""Same-source50/2 actual two changed renderer scopes; new24 and required compatibility26."""
import scoped_prometheus_post as post
import pg8724_full_metric_payload_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg8724-full-metric-payload-host-v1'
    post.RAW_SHA='8e87d9d6de971f04d11c47f1c9349d4359fe0c021b76068116dd307e31c81cd9'
    post.SLOT=post.host.W/'pg8726-full-metric-payload-post-v1'
    post.OUT=post.host.BASE/'PG8726-full-metric-payload-post-v1'
    assert post.SLOT.name.upper()==post.OUT.name.upper()
    api='dev/codex/schubert/nk/api/monitoring/'
    web='dev/codex/schubert/nk/web/monitoring/'
    post.MODULE='web'
    post.PREFIX=web
    post.NAMES={api+'ApiCustomMetricPayload',web+'WebCustomMetricPayload'}
    post.CLASS_MODULES={api+'ApiCustomMetricPayload':'api',api+'package-info':'api'}
    post.COMPONENT_METADATA={api+'package-info'}
    post.SOURCE_PATHS={'src/schubert-nk-'+role+'/src/main/java/dev/codex/schubert/nk/'+role+'/monitoring/'+title+'CustomMetricPayload.java' for role,title in (('api','Api'),('web','Web'))}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG8724-FULL-METRIC-PAYLOAD'
    post.main()
