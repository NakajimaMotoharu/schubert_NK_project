"""Original APIHOST16, exact new owner Main all four100 and unchanged quality policies."""
import scoped_prometheus_post as post
import pg8672_api_standard_source_host as original

if __name__ == '__main__':
    post.common.SOURCE=original.SOURCE
    post.common.COMPILE=original.COMPILE
    post.common.COMPILE_SHA=original.COMPILE_SHA
    post.RUN=post.host.W/'pg8672-api-standard-source-host-v1'
    post.RAW_SHA='a1bbf084aac789cd9d8ed7c6c9ca975bcc02fe917a127eb8da4651878fe5e781'
    post.SLOT=post.host.W/'pg8674-api-standard-source-post-v1'
    post.OUT=post.host.BASE/'PG8674-api-standard-source-post-v1'
    assert post.SLOT.name.upper()==post.OUT.name.upper()
    post.PREFIX='dev/codex/schubert/nk/api/monitoring/'
    post.MODULE='api'
    post.NAMES={post.PREFIX+'ApiStandardMetricSource'}
    post.SOURCE_PATHS={'src/schubert-nk-api/src/main/java/'+post.PREFIX+'ApiStandardMetricSource.java'}
    post.COUNTS=original.COUNTS
    post.GENERATED={}
    post.ENUM_TYPES=set()
    post.WITNESS_CASE_PREFIXES=()
    post.EXPECTED_SESSION='PG8672-API-STANDARD-SOURCE'
    post.main()
