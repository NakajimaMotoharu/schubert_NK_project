"""All1699 normal physical classes and current23/new valve, no historical coverage transfer."""
from types import SimpleNamespace
import pg7030_monitoring_six_compile as compile_library
import pg7102_web_http_six_post as post


if __name__=='__main__':
    post.compile_stage=SimpleNamespace(SOURCE='19c777bf3dbe3ddd0286d4c356a00ca8a47c99c5',
      SLOT=post.host.W/'pg7136-http-terminal-six-compile-v3',stage=compile_library)
    post.SLOT=post.host.W/'pg7142-http-terminal-six-post-v1'
    post.OUT=post.host.BASE/'PG7142-http-terminal-six-post-v1'
    post.PINS['currentHttp']=('PG7140-http-terminal-post-v2/manifest.json',
                             '1e66707fc37eef6842dda56ff945635b64f0d8ce0cab6a197b0b4ac0ed4a8653')
    post.PHYSICAL_COUNT=1699
    post.CURRENT_PHYSICAL_COUNT=10
    post.CURRENT_TESTS=23
    post.SOURCE_DELTA_COUNT=34
    post.ALLOW_CORE_POM_CHANGE=True
    post.main()
