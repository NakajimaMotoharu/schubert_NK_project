"""Original APIHOST16, exact new owner Main all four100 and unchanged quality policies."""
import scoped_prometheus_post as post
import pg8682_api_standard_source_fixed_host as original

if __name__ == '__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg8682-api-standard-source-fixed-host-v1'
    post.RAW_SHA='7ee64cce112888a61e5eb740ba3b5631621c6a672cadd0c5762a3695b3400bf8'
    post.SLOT=post.host.W/'pg8684-api-standard-source-fixed-post-v1'
    post.OUT=post.host.BASE/'PG8684-api-standard-source-fixed-post-v1'
    assert post.SLOT.name.upper()==post.OUT.name.upper()
    post.PREFIX='dev/codex/schubert/nk/api/monitoring/'
    post.MODULE='api'
    post.NAMES={post.PREFIX+'ApiStandardMetricSource'}
    post.SOURCE_PATHS={'src/schubert-nk-api/src/main/java/'+post.PREFIX+'ApiStandardMetricSource.java'}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG8682-API-STANDARD-SOURCE'
    post.main()
