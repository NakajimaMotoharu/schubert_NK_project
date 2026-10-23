"""All28 unchanged individual reasons, current169/42 positive qualification, no new raw finding."""
import pg6966_chr_adapter_host as host
from monitoring_increment_review import review

PINS={
 'current':('PG7288-transfer-health-post-v1/manifest.json','afac4559457cc1b93b359da1193d34d08558a868cf0513f5b2d9045a9d64da70'),
 'old':('PG7274-transfer-metric-post-v2/manifest.json','f167da99fa7062a2d890cd451dc99882b4ff553f1b041aec6b2087c7e4d6f876'),
 'oldReview':('PG7283-transfer-metric-review-v3/manifest.json','94b389bd75104dd55fd543de6973507ae412541d8c5c0af14a72938f998636c7'),
 'physical':('PG7292-transfer-health-six-post-v1/manifest.json','47ce5233888b5518fd0dc683dfbf29b8429a75adbc3439c4825d581ad12202ce'),
 'trace':('PG7294-transfer-health-trace-v1/manifest.json','422900508bcbdabcdf26f69a357bb93456b3cc44fdd76301662f7277198b33be'),
 'previous':('PG7280-transfer-metric-trace-v2/manifest.json','1975ccbc56108eff443fc9e3e067ae4440843e55e57edf4ad342c7a6d22fcdd3')}

if __name__=='__main__':
    review(entrypoint=__file__,out=host.BASE/'PG7296-transfer-health-review-v1',pins=PINS,
      source='74371ae0b185cee42e9b6930d68e34522640c2d6',tests=169,suites=23,executable=42,
      physical_count=1722,added_physical=53,anchor_counts=dict(changed=0,unchanged=59,introduced=2),
      new_class='TransferHealthMonitor',test_ids=['TRANSFERCONN001..008'],reason_document='018/1620',
      lock_methods=(),allow_no_new_findings=True)
