"""Original new32/2 and exact role-owner Main scopes, no historical counter transfer."""
import scoped_prometheus_post as post
import pg8712_web_batch_standard_source_host as original

if __name__=='__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg8712-web-batch-standard-source-host-v1'
    post.RAW_SHA='662cdf31cb7bfa58d464aca8fd10f3324fe7816e9d7e97e3436649fe04666eff'
    post.SLOT=post.host.W/'pg8714-web-batch-standard-source-post-v1'
    post.OUT=post.host.BASE/'PG8714-web-batch-standard-source-post-v1'
    assert post.SLOT.name.upper()==post.OUT.name.upper()
    web='dev/codex/schubert/nk/web/monitoring/'
    batch='dev/codex/schubert/nk/batch/monitoring/'
    post.MODULE='web'
    post.PREFIX=web
    post.NAMES={web+'WebStandardMetricSource',batch+'BatchStandardMetricSource'}
    post.CLASS_MODULES={batch+'BatchStandardMetricSource':'batch',batch+'package-info':'batch'}
    post.COMPONENT_METADATA={batch+'package-info'}
    post.SOURCE_PATHS={'src/schubert-nk-'+role+'/src/main/java/dev/codex/schubert/nk/'+role+'/monitoring/'+title+'StandardMetricSource.java' for role,title in (('web','Web'),('batch','Batch'))}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG8712-WEB-BATCH-STANDARD-SOURCE'
    post.main()
