"""Current API32 exact static/domain qualification, previous source bytes independently unchanged."""
import hashlib
import json
import subprocess
import pg7310_api_async_metric_review as review
import pg7338_api_async_collector_review as previous
import pg7352_api_pool_metric_six_compile as compilation

if __name__=='__main__':
    review.SOURCE=compilation.SOURCE;review.OUT=review.host.BASE/'PG7358-api-pool-metric-review-v1'
    review.CURRENT_TESTS=32;review.CURRENT_SUITES=4;review.CURRENT_EXECUTABLE=8
    review.PHYSICAL_COUNT=1731;review.ADDED_PHYSICAL=62
    review.PREVIOUS_COUNT=69;review.INTRODUCED_COUNT=2;review.CHANGED_COUNT=0
    previous.compilation=compilation;review.STATIC_CLASSIFIER=previous.classify
    review.PINS=dict(review.PINS)
    for key,path in {
      'currentApi':'PG7350-api-pool-metric-post-v1/manifest.json',
      'physical':'PG7354-api-pool-metric-six-post-v1/manifest.json',
      'trace':'PG7356-api-pool-metric-trace-v1/manifest.json',
      'previous':'PG7336-api-async-collector-trace-v1/manifest.json'}.items():
        review.PINS[key]=(path,review.host.sha(review.host.BASE/path))
    contract=json.loads((review.host.BASE/review.PINS['contract'][0]).read_bytes())
    inputs={'tools/quality/harnesses/monitoring-api-jobs-pom.xml':contract['harness']['apiSha256'],
      'tools/quality/harnesses/monitoring-pom.xml':contract['harness']['knownBatchSha256'],
      'src/schubert-nk-api/pom.xml':contract['apiPom']['sha256'],contract['canonicalDdl']['path']:contract['canonicalDdl']['sha256']}
    for path,digest in inputs.items():
        value=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=review.host.ROOT)
        review.require(hashlib.sha256(value).hexdigest()==digest,'unchanged twelve-guard input bytes only, not prior execution transfer')
    review.EXTRA_REVIEW=dict(contractInputHashes=inputs,allPrevious69SourceBytesUnchanged=True,
      newPoolMetricRawFindings=0,actualHikariPoolOrManagementCalls=0)
    review.main()
