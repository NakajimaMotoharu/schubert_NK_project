"""Exact current SDK15 classes and one reviewed compile dependency; historical domains not transferred."""
import pg7102_web_http_six_post as post
import pg7120_micrometer_http_six_compile as compile_stage


if __name__=='__main__':
    post.compile_stage=compile_stage
    post.SLOT=post.host.W/'pg7122-micrometer-http-six-post-v1'
    post.OUT=post.host.BASE/'PG7122-micrometer-http-six-post-v1'
    post.PINS['currentHttp']=('PG7118-micrometer-http-post-v3/manifest.json',
                             '0aa4cee63e3f64d8b0439edd8b6da776f8a3bd9466e4dbc714f3c28ae7f7518b')
    post.PHYSICAL_COUNT=1697
    post.CURRENT_PHYSICAL_COUNT=8
    post.CURRENT_TESTS=15
    post.SOURCE_DELTA_COUNT=32
    post.ALLOW_CORE_POM_CHANGE=True
    post.main()
