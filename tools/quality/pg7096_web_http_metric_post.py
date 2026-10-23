"""Independent six-class HTTP label contract CRC/session/counter and static post."""
import pg7008_monitoring_mode_post as post
import pg7094_web_http_metric_host as host

METHODS={'httpMetric001ApprovedCatalogModesAndBuckets','httpMetric002IndependentWholeFiniteLabelMatrix',
 'httpMetric003UnknownUserValuesCannotGrowLabelSpace','httpMetric004NullUnknownAndStatusBoundariesAreExplicit',
 'httpMetric005AllReturnedCollectionsAreImmutable','httpMetric006ConcurrentClassifiersAreStateless'}


if __name__=='__main__':
    post.SLOT=host.SLOT
    post.POM=host.POM
    post.RUN='PG7094-web-http-metric-host-v1'
    post.OUT=post.host.BASE/'PG7096-web-http-metric-post-v1'
    post.PRIVATE=post.host.W/'pg7096-web-http-metric-post-v1'
    post.PREFIX='dev/codex/schubert/nk/web/monitoring/'
    post.NAMES={post.PREFIX+'HttpMetricContract'+suffix for suffix in ('','$Metric','$Route','$Method','$Status','$Labels')}
    post.SOURCE_ROOT_PREFIX='src/schubert-nk-web/'
    post.SOURCE_FILE_COUNT=3
    post.METHODS=METHODS
    post.TOTAL_TESTS=6
    post.EXPECTED_SUITES={host.SUITE:dict(tests=6,failures=0,errors=0,skipped=0)}
    post.main()
