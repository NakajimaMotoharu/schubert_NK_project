"""Register reviewed24 Web boundary source primaries; no actual runtime acceptance."""
from pathlib import Path
import explicit_primary_source_registration as register
import trace_owner_join_web_boundary24 as resolver

if __name__=='__main__':
    register.run(Path(__file__),resolver,register.BASE/'PG9450-web-boundary24-source-join-v1',
      'PG9438-api-jms20-source-join-v1/manifest.json','0eb6d96826969b6f605e4001e738c0f4ab802ce3f6cfbe734f2811ecdf41fd88',
      'PG9448-web-boundary24-source-post-v1/manifest.json','4668707b55bbc9eb99e307f3f99583c3736785e2614f7ef3c1b4f3bd4ca2d914',24,1610)
