"""Register22 Web screen/form/view source primaries; preserve all old related/runtime fields."""
from pathlib import Path
import explicit_primary_source_registration as register
import trace_owner_join_web_screen22 as resolver

if __name__=='__main__':
    register.run(Path(__file__),resolver,register.BASE/'PG9462-web-screen22-source-join-v1',
      'PG9450-web-boundary24-source-join-v1/manifest.json','170288a0dc7c8b2ebecd8bd42c397bdfdc274f30057c8c2c7dc850063afe5818',
      'PG9460-web-screen22-source-post-v1/manifest.json','704d0f881f083a44cb746e2dcc4a1fb77ac61c47259137747bc51830703d5008',22,1632)
