"""Current169/Batch43 physical, old1669 unchanged and exact two POM semantic changes."""
import pg7158_filesystem_health_six_post as post
import pg7290_transfer_health_six_compile as compilation
from batch_metric_pom_contract import verify_batch_core_pom

if __name__=='__main__':
    post.compilation=compilation
    post.SLOT=post.host.W/'pg7292-transfer-health-six-post-v1'
    post.OUT=post.host.BASE/'PG7292-transfer-health-six-post-v1'
    post.POM_REVIEWERS={
      'src/schubert-nk-web/pom.xml':post.pom_contract.verify_core_pom,
      'src/schubert-nk-batch/pom.xml':verify_batch_core_pom}
    post.PINS['currentBatch']=('PG7288-transfer-health-post-v1/manifest.json',
        'afac4559457cc1b93b359da1193d34d08558a868cf0513f5b2d9045a9d64da70')
    post.CURRENT_TESTS=169;post.CURRENT_SUITES=23;post.CURRENT_PHYSICAL=43
    post.PHYSICAL_COUNT=1722;post.SOURCE_DELTA_COUNT=61
    post.main()
