"""All75 sources/64 added physical, currentAPI10 only; unchanged71 plus new observation connection4."""
import pg7308_api_async_metric_trace as trace
import pg7366_api_pool_observation_six_compile as compilation

if __name__=='__main__':
    trace.SOURCE=compilation.SOURCE
    trace.OUT=trace.host.BASE/'PG7370-api-pool-observation-trace-v1'
    trace.SOURCE_COUNT=75;trace.PREVIOUS_COUNT=71
    trace.CURRENT_TESTS=48;trace.CURRENT_SUITES=6
    trace.CURRENT_EXECUTABLE=10;trace.ADDED_PHYSICAL=64
    trace.SPEC_ID=1639;trace.RESULT_ID=1640;trace.PHYSICAL_DOC_ID=1641
    trace.DOCS={1639:'1639_APIPool観測結線_単体テスト仕様書.md',
      1640:'1640_APIPool観測結線_実行結果.md',1641:'1641_APIPool観測結線_実Jar・資格domain.md'}
    trace.TEST_ID_FAMILY='POOLREAD001..008/POOLCONN001..008'
    trace.ALLOWED_NEW={'DbPoolMetricObservation.java','DbPoolMetricObservationTest.java',
                       'DbPoolMetricCollector.java','DbPoolMetricCollectorTest.java'}
    trace.PINS={
      'currentApi':('PG7364-api-pool-observation-post-v1/manifest.json',None),
      'physical':('PG7368-api-pool-observation-six-post-v1/manifest.json',None),
      'previous':('PG7356-api-pool-metric-trace-v1/manifest.json','5cbd957e931f7e9fb41dc674fdd175ccb1c491a855d8202891af52dc85f4a0e1')}
    trace.PINS={k:(p,h or trace.host.sha(trace.host.BASE/p)) for k,(p,h) in trace.PINS.items()}
    trace.main()
