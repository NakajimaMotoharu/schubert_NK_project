"""All27 raw PMD applicability/52 provenance rows, no PT replay or acceptance update."""
import pg6966_chr_adapter_host as host
from monitoring_increment_review import review

PINS={
 'current':('PG7240-sync-p95-post-v1/manifest.json','9f33517809137a97dd1bb9aabe638d9ca214ab834658b5df4d025119069b33c1'),
 'old':('PG7226-db-pool-post-v1/manifest.json','bd2cc87daab25d573fad196fcaff81c2f7d7fa63d8ccfea2ba850779729956d4'),
 'oldReview':('PG7234-db-pool-review-v1/manifest.json','e400ed27ccf0d5efa94f0a2dc2bd8070debb47c245f51c1cd7739f067ae4f7d8'),
 'physical':('PG7244-sync-p95-six-post-v1/manifest.json','8262e923c7a559d0e8e4744a5daa8469f481744401776c926e7ba26872557e6d'),
 'trace':('PG7246-sync-p95-trace-v1/manifest.json','6422d1e9859fe7a5ddd8ac4ca3c4f21ffec9d0aa7a68e5b0b5738b275d294d02'),
 'previous':('PG7232-db-pool-trace-v1/manifest.json','49f9452d76b058f3efdf84738b7eb2920744b73ac54c9bab1f39d13e1cf59b62')}

if __name__=='__main__':
    review(entrypoint=__file__,out=host.BASE/'PG7248-sync-p95-review-v1',pins=PINS,
      source='00edd88adbff2625fdd479224e0d3a12bd188861',tests=140,suites=19,executable=32,
      physical_count=1712,added_physical=43,anchor_counts=dict(changed=0,unchanged=50,introduced=2),
      new_class='TimedSyncLatencyMonitor',test_ids=['SYNCTIME007'],reason_document='018/1608')
