"""Current72 with unchanged Main bytes, exact whole1738/currentAPI16, no old execution transfer."""
import pg7306_api_async_metric_six_post as post
import pg7406_api_generated_contract_six_compile as compilation
import pg7362_api_pool_observation_host as host

if __name__=='__main__':
    post.compilation=compilation
    post.SLOT=post.host.W/'pg7408-api-generated-contract-six-post-v1'
    post.OUT=post.host.BASE/'PG7408-api-generated-contract-six-post-v1'
    post.PINS=dict(post.PINS)
    path='PG7404-api-generated-contract-post-v1/manifest.json'
    post.PINS['currentApi']=(path,post.host.sha(post.host.BASE/path))
    post.CURRENT_TESTS=72;post.CURRENT_SUITES=9;post.CURRENT_PHYSICAL=16
    post.PHYSICAL_COUNT=1738;post.SOURCE_DELTA_COUNT=80
    post.EXTRA_CURRENT_AUXILIARY_JARS=host.EXTRA
    post.main()
