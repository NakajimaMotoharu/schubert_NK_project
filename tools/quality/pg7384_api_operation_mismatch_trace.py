"""All77 source/66 added physical, unchanged75 and new metric Main/Test only."""
import pg7308_api_async_metric_trace as trace
import pg7380_api_operation_mismatch_six_compile as compilation

if __name__=='__main__':
    trace.SOURCE=compilation.SOURCE
    trace.OUT=trace.host.BASE/'PG7384-api-operation-mismatch-trace-v1'
    trace.SOURCE_COUNT=77;trace.PREVIOUS_COUNT=75
    trace.CURRENT_TESTS=56;trace.CURRENT_SUITES=7
    trace.CURRENT_EXECUTABLE=12;trace.ADDED_PHYSICAL=66
    trace.SPEC_ID=1643;trace.RESULT_ID=1644;trace.PHYSICAL_DOC_ID=1645
    trace.DOCS={1643:'1643_APIOperationMismatchMetric_単体テスト仕様書.md',
      1644:'1644_APIOperationMismatchMetric_実行結果.md',1645:'1645_APIOperationMismatchMetric_実Jar・資格domain.md'}
    trace.TEST_ID_FAMILY='OPMIS001..008'
    trace.ALLOWED_NEW={'OperationMismatchMetricRecorder.java','OperationMismatchMetricRecorderTest.java'}
    trace.PINS={
      'currentApi':('PG7378-api-operation-mismatch-post-v1/manifest.json',None),
      'physical':('PG7382-api-operation-mismatch-six-post-v1/manifest.json',None),
      'previous':('PG7370-api-pool-observation-trace-v1/manifest.json','4fbb15d1966ed3c60032602f6f6444d02d754f8d485c861683563b8cccc4ee7d')}
    trace.PINS={k:(p,h or trace.host.sha(trace.host.BASE/p)) for k,(p,h) in trace.PINS.items()}
    trace.main()
