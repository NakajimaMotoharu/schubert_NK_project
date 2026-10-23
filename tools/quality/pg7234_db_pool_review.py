"""All25 raw PMD applicability and50 provenance rows, no PT replay or acceptance update."""
import pg6966_chr_adapter_host as host
from monitoring_increment_review import review

PINS={
 'current':('PG7226-db-pool-post-v1/manifest.json','bd2cc87daab25d573fad196fcaff81c2f7d7fa63d8ccfea2ba850779729956d4'),
 'old':('PG7212-heap-connection-post-v1/manifest.json','f42c119d34dbe54c5c22f8f75f0d1b1eab80f20b648c419c4ba9d6138e50aa58'),
 'oldReview':('PG7220-heap-connection-review-v1/manifest.json','247edc2bbb450f1942a0e5f6284190e964ce8f080716a2e4fd0c0d6ef835170a'),
 'physical':('PG7230-db-pool-six-post-v1/manifest.json','4d3d8a5dbbac6e21fab22b12799467b8ed9af3c1439eb23a87a7477241015a2a'),
 'trace':('PG7232-db-pool-trace-v1/manifest.json','49f9452d76b058f3efdf84738b7eb2920744b73ac54c9bab1f39d13e1cf59b62'),
 'previous':('PG7218-heap-connection-trace-v1/manifest.json','763e8d9e96b4f05e99c8983838fc5c2b5a592d84c50869815407a609690eea71')}

if __name__=='__main__':
    review(entrypoint=__file__,out=host.BASE/'PG7234-db-pool-review-v1',pins=PINS,
      source='e9c0ba2a180262f8410ae16c46f5909787b5132b',tests=132,suites=18,executable=30,
      physical_count=1710,added_physical=41,anchor_counts=dict(changed=0,unchanged=48,introduced=2),
      new_class='TimedDbPoolMonitor',test_ids=['DBTIME007'],reason_document='018/1604')
