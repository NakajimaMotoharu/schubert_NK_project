"""All67 declared source paths, currentAPI4 vs historical byte-only Batch/Web."""
import pg7308_api_async_metric_trace as trace
import pg7318_api_async_count_six_compile as compilation

if __name__=='__main__':
    trace.SOURCE=compilation.SOURCE
    trace.OUT=trace.host.BASE/'PG7322-api-async-count-trace-v1'
    trace.SOURCE_COUNT=67;trace.PREVIOUS_COUNT=65
    trace.CURRENT_TESTS=16;trace.CURRENT_SUITES=2
    trace.CURRENT_EXECUTABLE=4;trace.ADDED_PHYSICAL=58
    trace.SPEC_ID=1627;trace.RESULT_ID=1628;trace.PHYSICAL_DOC_ID=1629
    trace.DOCS={1627:'1627_APIAsyncJobCountSource_単体テスト仕様書.md',
      1628:'1628_APIAsyncJobCountSource_実行結果.md',1629:'1629_APIAsyncJobCountSource_実Jar・資格domain.md'}
    trace.TEST_ID_FAMILY='ASYNCDB001..008'
    trace.ALLOWED_NEW={'AsyncJobCountRepository.java','AsyncJobCountRepositoryTest.java'}
    trace.PINS={
      'currentApi':('PG7316-api-async-count-post-v1/manifest.json',None),
      'physical':('PG7320-api-async-count-six-post-v1/manifest.json',None),
      'previous':('PG7308-api-async-metric-trace-v1/manifest.json','381d93ed6e22bece84f3eee23d09a5c6bb37201e741a8e79a43dda34f5bf14ca')}
    trace.PINS={k:(p,h or trace.host.sha(trace.host.BASE/p)) for k,(p,h) in trace.PINS.items()}
    trace.main()
