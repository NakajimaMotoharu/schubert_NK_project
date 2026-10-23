"""All71 sources/62 added physical, currentAPI8 only and all previous69 source bytes unchanged."""
import pg7308_api_async_metric_trace as trace
import pg7352_api_pool_metric_six_compile as compilation

if __name__=='__main__':
    trace.SOURCE=compilation.SOURCE
    trace.OUT=trace.host.BASE/'PG7356-api-pool-metric-trace-v1'
    trace.SOURCE_COUNT=71;trace.PREVIOUS_COUNT=69
    trace.CURRENT_TESTS=32;trace.CURRENT_SUITES=4
    trace.CURRENT_EXECUTABLE=8;trace.ADDED_PHYSICAL=62
    trace.SPEC_ID=1635;trace.RESULT_ID=1636;trace.PHYSICAL_DOC_ID=1637
    trace.DOCS={1635:'1635_APIDbPoolMetric_単体テスト仕様書.md',
      1636:'1636_APIDbPoolMetric_実行結果.md',1637:'1637_APIDbPoolMetric_実Jar・資格domain.md'}
    trace.TEST_ID_FAMILY='POOLMET001..008'
    trace.ALLOWED_NEW={'DbPoolMetricRecorder.java','DbPoolMetricRecorderTest.java'}
    trace.PINS={
      'currentApi':('PG7350-api-pool-metric-post-v1/manifest.json',None),
      'physical':('PG7354-api-pool-metric-six-post-v1/manifest.json',None),
      'previous':('PG7336-api-async-collector-trace-v1/manifest.json','bf0ba9a4445e5571d878c902ce1cb4c2c9fe43b27eb06f6641d1564f560d031e')}
    trace.PINS={k:(p,h or trace.host.sha(trace.host.BASE/p)) for k,(p,h) in trace.PINS.items()}
    trace.main()
