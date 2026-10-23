"""All79 sources/69 added physical, currentAPI15 and previous77 source bytes unchanged."""
import pg7308_api_async_metric_trace as trace
import pg7394_api_outbox_rows_six_compile as compilation

if __name__=='__main__':
    trace.SOURCE=compilation.SOURCE
    trace.OUT=trace.host.BASE/'PG7398-api-outbox-rows-trace-v1'
    trace.SOURCE_COUNT=79;trace.PREVIOUS_COUNT=77
    trace.CURRENT_TESTS=64;trace.CURRENT_SUITES=8
    trace.CURRENT_EXECUTABLE=15;trace.ADDED_PHYSICAL=69
    trace.SPEC_ID=1647;trace.RESULT_ID=1648;trace.PHYSICAL_DOC_ID=1649
    trace.DOCS={1647:'1647_APIOutboxRowsMetric_単体テスト仕様書.md',
      1648:'1648_APIOutboxRowsMetric_実行結果.md',1649:'1649_APIOutboxRowsMetric_実Jar・資格domain.md'}
    trace.TEST_ID_FAMILY='OUTBOXMET001..008'
    trace.ALLOWED_NEW={'OutboxRowsMetricRecorder.java','OutboxRowsMetricRecorderTest.java'}
    trace.PINS={
      'currentApi':('PG7392-api-outbox-rows-post-v1/manifest.json',None),
      'physical':('PG7396-api-outbox-rows-six-post-v1/manifest.json',None),
      'previous':('PG7384-api-operation-mismatch-trace-v1/manifest.json','8ab934f15c7fd08fc19059c0286c0392fceb48e4c6225ae4b1a0890bd122005b')}
    trace.PINS={k:(p,h or trace.host.sha(trace.host.BASE/p)) for k,(p,h) in trace.PINS.items()}
    trace.main()
