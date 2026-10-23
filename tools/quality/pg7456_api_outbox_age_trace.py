"""CurrentAPI80 and all84 changed source owners; generated oracle and prior-role histories separate."""
import pg7308_api_async_metric_trace as trace
import pg7452_api_outbox_age_six_compile as compilation

if __name__=='__main__':
    trace.SOURCE=compilation.SOURCE;trace.OUT=trace.host.BASE/'PG7456-api-outbox-age-trace-v1'
    trace.SOURCE_COUNT=84;trace.PREVIOUS_COUNT=82
    trace.CURRENT_TESTS=80;trace.CURRENT_SUITES=10;trace.CURRENT_EXECUTABLE=17;trace.ADDED_PHYSICAL=71
    trace.SPEC_ID=1660;trace.RESULT_ID=1661;trace.PHYSICAL_DOC_ID=1662
    trace.DOCS={1660:'1660_APIOutboxAgeMetric_単体テスト仕様書.md',1661:'1661_APIOutboxAgeMetric_実行結果.md',
      1662:'1662_APIOutboxAgeMetric_品質・追跡.md'}
    trace.TEST_ID_FAMILY='OUTBOXAGE001..008'
    trace.ALLOWED_NEW={'OutboxAgeMetricRecorder.java','OutboxAgeMetricRecorderTest.java'}
    trace.PINS={
      'currentApi':('PG7450-api-outbox-age-post-v1/manifest.json',None),
      'physical':('PG7454-api-outbox-age-six-post-v1/manifest.json',None),
      'previous':('PG7442-web-generated-byte-trace-v1/manifest.json','976417dff5cf31223ebf5593a59581e95fe7321af9c144a68a18a8194e360041')}
    trace.PINS={k:(p,h or trace.host.sha(trace.host.BASE/p)) for k,(p,h) in trace.PINS.items()}
    trace.main()
