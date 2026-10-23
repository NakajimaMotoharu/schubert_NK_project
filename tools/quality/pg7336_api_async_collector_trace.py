"""All69 source paths/current API5, exact one declared fixture edit and two new files."""
import pg7308_api_async_metric_trace as trace
import pg7344_api_collector_owned_registry_six_compile as compilation

if __name__=='__main__':
    trace.SOURCE=compilation.SOURCE
    trace.OUT=trace.host.BASE/'PG7336-api-async-collector-trace-v1'
    trace.SOURCE_COUNT=69;trace.PREVIOUS_COUNT=67
    trace.CURRENT_TESTS=24;trace.CURRENT_SUITES=3
    trace.CURRENT_EXECUTABLE=5;trace.ADDED_PHYSICAL=59
    trace.SPEC_ID=1631;trace.RESULT_ID=1632;trace.PHYSICAL_DOC_ID=1633
    trace.DOCS={1631:'1631_APIAsyncCountMetric結線_単体テスト仕様書.md',
      1632:'1632_APIAsyncCountMetric結線_実行結果.md',1633:'1633_APIAsyncCountMetric結線_実Jar・資格domain.md'}
    trace.TEST_ID_FAMILY='ASYNCCONN001..008'
    trace.ALLOWED_NEW={'AsyncJobMetricCollector.java','AsyncJobMetricCollectorTest.java'}
    trace.EDITED_EXISTING={'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/AsyncJobCountRepositoryTest.java'}
    trace.PINS={
      'currentApi':('PG7342-api-collector-owned-registry-post-v1/manifest.json',None),
      'physical':('PG7334-api-async-collector-six-post-v1/manifest.json',None),
      'previous':('PG7322-api-async-count-trace-v1/manifest.json','c44ff53ed3bad8c37f37d2f686c1cef8e4709ab90f268b2ee3f31c912687bc2d')}
    trace.PINS={k:(p,h or trace.host.sha(trace.host.BASE/p)) for k,(p,h) in trace.PINS.items()}
    trace.main()
