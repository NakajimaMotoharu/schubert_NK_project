"""Exact declared new13 PT/4 executable classes; original mode result stays historical."""
import pg7008_monitoring_mode_post as post
import pg7012_metric_catalog_host as host

METHODS = {
 'metric001CompleteIndependentCatalog','metric002UnknownMissingAndAliasedNamesRejected',
 'metric003ExactLabelNamesNoImplicitOrSensitiveKeys','metric004NoMutableStateExposureOrRetention',
 'metric005IndependentHttpBucketsAndImmutableResult','metric006ConcurrentCallersObserveOnlyOriginalCatalog'}


if __name__ == '__main__':
    post.SLOT = host.SLOT
    post.RUN = 'PG7012-metric-catalog-host-v1'
    post.OUT = post.host.BASE/'PG7014-metric-catalog-post-v1'
    post.PRIVATE = post.host.W/'pg7014-metric-catalog-post-v1'
    post.NAMES = post.NAMES | {post.PREFIX+'MetricContract', post.PREFIX+'MetricContract$Kind'}
    post.METHODS = post.METHODS | METHODS
    post.EXPECTED_SUITES = {host.SUITES[0]:dict(tests=7,failures=0,errors=0,skipped=0),
                           host.SUITES[1]:dict(tests=6,failures=0,errors=0,skipped=0)}
    post.TOTAL_TESTS = 13
    post.SOURCE_FILE_COUNT = 5
    post.main()
