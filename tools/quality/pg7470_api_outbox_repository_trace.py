"""All86 source owners/currentAPI90, historical Batch/Web byte-only, no acceptance synthesis."""
import pg7308_api_async_metric_trace as trace
import pg7466_api_outbox_repository_six_compile as compilation

if __name__=='__main__':
    trace.SOURCE=compilation.SOURCE;trace.OUT=trace.host.BASE/'PG7470-api-outbox-repository-trace-v1'
    trace.SOURCE_COUNT=86;trace.PREVIOUS_COUNT=84
    trace.CURRENT_TESTS=90;trace.CURRENT_SUITES=11;trace.CURRENT_EXECUTABLE=19;trace.ADDED_PHYSICAL=73
    trace.SPEC_ID=1664;trace.RESULT_ID=1665;trace.PHYSICAL_DOC_ID=1666
    trace.DOCS={1664:'1664_APIOutbox観測Repository_単体テスト仕様書.md',1665:'1665_APIOutbox観測Repository_実行結果.md',
      1666:'1666_APIOutbox観測Repository_品質・追跡.md'}
    trace.TEST_ID_FAMILY='OUTBOXDB001..010'
    trace.ALLOWED_NEW={'OutboxObservationRepository.java','OutboxObservationRepositoryTest.java'}
    trace.PINS={
      'currentApi':('PG7464-api-outbox-repository-post-v1/manifest.json',None),
      'physical':('PG7468-api-outbox-repository-six-post-v1/manifest.json',None),
      'previous':('PG7456-api-outbox-age-trace-v1/manifest.json','6a8e3087d1b4a6ff19f25a565b410965b4bf398013e01c8130484fc65db318b6')}
    trace.PINS={k:(p,h or trace.host.sha(trace.host.BASE/p)) for k,(p,h) in trace.PINS.items()}
    trace.main()
