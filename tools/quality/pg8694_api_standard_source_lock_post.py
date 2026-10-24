"""Original APIHOST16, exact new owner Main all four100 and unchanged quality policies."""
import scoped_prometheus_post as post
import pg8692_api_standard_source_lock_host as original

if __name__ == '__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg8692-api-standard-source-lock-host-v1'
    post.RAW_SHA='cdd1aaad4e5b6adc6783a4474e6c66b0d02b3bfcfbd7f5e04cc95b580870e1de'
    post.SLOT=post.host.W/'pg8694-api-standard-source-lock-post-v1'
    post.OUT=post.host.BASE/'PG8694-api-standard-source-lock-post-v1'
    assert post.SLOT.name.upper()==post.OUT.name.upper()
    post.PREFIX='dev/codex/schubert/nk/api/monitoring/'
    post.MODULE='api'
    post.NAMES={post.PREFIX+'ApiStandardMetricSource'}
    post.SOURCE_PATHS={'src/schubert-nk-api/src/main/java/'+post.PREFIX+'ApiStandardMetricSource.java'}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG8692-API-STANDARD-SOURCE'
    post.main()
