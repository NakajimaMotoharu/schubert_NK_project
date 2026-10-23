"""All80 source/69 added physical; explicit generated-type oracle supplements, no original PT transfer."""
import pg7308_api_async_metric_trace as trace
import pg7406_api_generated_contract_six_compile as compilation

if __name__=='__main__':
    trace.SOURCE=compilation.SOURCE
    trace.OUT=trace.host.BASE/'PG7410-api-generated-contract-trace-v1'
    trace.SOURCE_COUNT=80;trace.PREVIOUS_COUNT=77
    trace.CURRENT_TESTS=72;trace.CURRENT_SUITES=9
    trace.CURRENT_EXECUTABLE=15;trace.ADDED_PHYSICAL=69
    trace.SPEC_ID=1647;trace.RESULT_ID=1651;trace.PHYSICAL_DOC_ID=1652
    trace.DOCS={1647:'1647_APIOutboxRowsMetric_単体テスト仕様書.md',
      1650:'1650_API生成Value契約_追加単体テスト仕様書.md',
      1651:'1651_API生成Value契約_実行結果.md',1652:'1652_API生成Value契約_実Jar・品質追跡.md'}
    trace.TEST_ID_FAMILY='OUTBOXMET001..008'
    trace.ALLOWED_NEW={'OutboxRowsMetricRecorder.java','OutboxRowsMetricRecorderTest.java','GeneratedMetricValueContractTest.java'}
    trace.NEW_SOURCE_CONTRACTS={'GeneratedMetricValueContractTest.java':('GENMET001..008',1650)}
    prefix='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/'
    trace.ADDITIONAL_SPEC_IDS_BY_PATH={prefix+name:(1650,) for name in (
      'AsyncJobMetricRecorder.java','DbPoolMetricRecorder.java',
      'OperationMismatchMetricRecorder.java','OutboxRowsMetricRecorder.java')}
    trace.PINS={
      'currentApi':('PG7404-api-generated-contract-post-v1/manifest.json',None),
      'physical':('PG7408-api-generated-contract-six-post-v1/manifest.json',None),
      'previous':('PG7384-api-operation-mismatch-trace-v1/manifest.json','8ab934f15c7fd08fc19059c0286c0392fceb48e4c6225ae4b1a0890bd122005b')}
    trace.PINS={k:(p,h or trace.host.sha(trace.host.BASE/p)) for k,(p,h) in trace.PINS.items()}
    trace.main()
