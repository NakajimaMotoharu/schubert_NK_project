"""Current153/Batch37 physical and old1669 byte identity, exact two POM dependency nodes."""
import pg7158_filesystem_health_six_post as post
import pg7256_batch_metric_six_compile as compilation
from batch_metric_pom_contract import verify_batch_core_pom

if __name__=='__main__':
    post.compilation=compilation
    post.SLOT=post.host.W/'pg7258-batch-metric-six-post-v1'
    post.OUT=post.host.BASE/'PG7258-batch-metric-six-post-v1'
    post.POM_REVIEWERS={
      'src/schubert-nk-web/pom.xml':post.pom_contract.verify_core_pom,
      'src/schubert-nk-batch/pom.xml':verify_batch_core_pom}
    post.PINS['currentBatch']=('PG7254-batch-metric-post-v1/manifest.json',
        '379cef1807e526b900bd9ff61c1fd96224bad8be09e355862133adad7f34bc9a')
    post.CURRENT_TESTS=153;post.CURRENT_SUITES=21;post.CURRENT_PHYSICAL=37
    post.PHYSICAL_COUNT=1716;post.SOURCE_DELTA_COUNT=57
    post.main()
