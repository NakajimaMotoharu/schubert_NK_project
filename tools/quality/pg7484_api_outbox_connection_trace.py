"""All88 source owners/currentAPI98 and historical Batch/Web byte-only, no coverage union."""
import pg7308_api_async_metric_trace as trace
import pg7480_api_outbox_connection_six_compile as compilation

if __name__=='__main__':
    trace.SOURCE=compilation.SOURCE;trace.OUT=trace.host.BASE/'PG7484-api-outbox-connection-trace-v1'
    trace.SOURCE_COUNT=88;trace.PREVIOUS_COUNT=86
    trace.CURRENT_TESTS=98;trace.CURRENT_SUITES=12;trace.CURRENT_EXECUTABLE=20;trace.ADDED_PHYSICAL=74
    trace.SPEC_ID=1668;trace.RESULT_ID=1669;trace.PHYSICAL_DOC_ID=1670
    trace.DOCS={1668:'1668_APIOutboxMetric結線_単体テスト仕様書.md',1669:'1669_APIOutboxMetric結線_実行結果.md',
      1670:'1670_APIOutboxMetric結線_品質・追跡.md'}
    trace.TEST_ID_FAMILY='OUTBOXCONN001..008'
    trace.ALLOWED_NEW={'OutboxMetricCollector.java','OutboxMetricCollectorTest.java'}
    trace.PINS={
      'currentApi':('PG7478-api-outbox-connection-post-v1/manifest.json',None),
      'physical':('PG7482-api-outbox-connection-six-post-v1/manifest.json',None),
      'previous':('PG7470-api-outbox-repository-trace-v1/manifest.json','ba3df20750f5a4c1454dbdbba5f3ddc4e962240674659bc9a8cbecb656a3839d')}
    trace.PINS={k:(p,h or trace.host.sha(trace.host.BASE/p)) for k,(p,h) in trace.PINS.items()}
    trace.main()
