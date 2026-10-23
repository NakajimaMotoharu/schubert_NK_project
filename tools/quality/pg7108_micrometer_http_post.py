"""Same original15 tests/current7 executable classes and exact SDK/static classpath binding."""
import pg7008_monitoring_mode_post as post
import pg7096_web_http_metric_post as metadata
import pg7106_micrometer_http_host as host

METHODS={'httpRec001StandardDoesNotRegisterOrClose','httpRec002ActualMeterNamesTagsAndNineSlos',
 'httpRec003WholeIndependentMatrixHasExactCounts','httpRec004UnknownInputsCannotCreateSeries',
 'httpRec005InvalidAndSingleMaximumBoundaries','httpRec006ProviderFailuresAreNotNormalizedOrRetried',
 'httpRec007ConcurrentActualProviderCounts','httpRec008BorrowedOwnerAndExternalMeterRemainUntouched',
 'httpRec009WrongTypeIsRejectedWithoutAlternativeIdentity'}


if __name__=='__main__':
    post.SLOT=host.SLOT
    post.POM=host.POM
    post.RUN='PG7106-micrometer-http-host-v1'
    post.OUT=post.host.BASE/'PG7108-micrometer-http-post-v1'
    post.PRIVATE=post.host.W/'pg7108-micrometer-http-post-v1'
    post.PREFIX='dev/codex/schubert/nk/web/monitoring/'
    post.NAMES={post.PREFIX+'HttpMetricContract'+suffix for suffix in ('','$Metric','$Route','$Method','$Status','$Labels')}
    post.NAMES.add(post.PREFIX+'HttpMetricRecorder')
    post.SOURCE_ROOT_PREFIX='src/schubert-nk-web/'
    post.SOURCE_FILE_COUNT=5
    post.METHODS=metadata.METHODS|METHODS
    post.TOTAL_TESTS=15
    post.EXPECTED_SUITES={name:dict(tests=count,failures=0,errors=0,skipped=0)
                         for name,count in zip(host.SUITES,(6,9),strict=True)}
    post.EXTRA_AUXILIARY_JARS=host.SDK
    post.main()
