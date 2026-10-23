"""Fixed-source161/Batch41 physical, old1669 unchanged and exact two declared POM changes."""
import pg7158_filesystem_health_six_post as post
import pg7276_transfer_metric_six_compile_v2 as compilation
from batch_metric_pom_contract import verify_batch_core_pom

if __name__=='__main__':
    post.compilation=compilation
    post.SLOT=post.host.W/'pg7278-transfer-metric-six-post-v2'
    post.OUT=post.host.BASE/'PG7278-transfer-metric-six-post-v2'
    post.POM_REVIEWERS={
      'src/schubert-nk-web/pom.xml':post.pom_contract.verify_core_pom,
      'src/schubert-nk-batch/pom.xml':verify_batch_core_pom}
    post.PINS['currentBatch']=('PG7274-transfer-metric-post-v2/manifest.json',
        'f167da99fa7062a2d890cd451dc99882b4ff553f1b041aec6b2087c7e4d6f876')
    post.CURRENT_TESTS=161;post.CURRENT_SUITES=22;post.CURRENT_PHYSICAL=41
    post.PHYSICAL_COUNT=1720;post.SOURCE_DELTA_COUNT=59
    post.main()
