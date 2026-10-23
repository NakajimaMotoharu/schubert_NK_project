"""All28 raw PMD rows/57 source anchors; one new recorder lock only, no PT replay."""
import pg6966_chr_adapter_host as host
from monitoring_increment_review import review

PINS={
 'current':('PG7254-batch-metric-post-v1/manifest.json','379cef1807e526b900bd9ff61c1fd96224bad8be09e355862133adad7f34bc9a'),
 'old':('PG7240-sync-p95-post-v1/manifest.json','9f33517809137a97dd1bb9aabe638d9ca214ab834658b5df4d025119069b33c1'),
 'oldReview':('PG7248-sync-p95-review-v1/manifest.json','d9ff6d1a3e57b53783cafc27bd976669226340534b2751eecb04e7f7e19d2a99'),
 'physical':('PG7258-batch-metric-six-post-v1/manifest.json','8546601af65ecfb0de5e57f460349651bcfc6ab8a242ee9b9725b3c87d283866'),
 'trace':('PG7260-batch-metric-trace-v1/manifest.json','90ad5b48b1fd626d4e52dc103e90bd551a07248764b8f2d4a82e581815d1674b'),
 'previous':('PG7246-sync-p95-trace-v1/manifest.json','6422d1e9859fe7a5ddd8ac4ca3c4f21ffec9d0aa7a68e5b0b5738b275d294d02')}

if __name__=='__main__':
    review(entrypoint=__file__,out=host.BASE/'PG7262-batch-metric-review-v1',pins=PINS,
      source='34813cef90b2a5c6b2ad3be835565bf53e96a875',tests=153,suites=21,executable=36,
      physical_count=1716,added_physical=47,anchor_counts=dict(changed=0,unchanged=52,introduced=5),
      new_class='BatchMetricRecorder',test_ids=['BATCHREC006','BATCHREC007'],reason_document='018/1612',lock_methods=('record',))
