"""Register42 exact API/Web source responsibilities, preserving all historical results."""
from pathlib import Path
import explicit_primary_source_registration as register
import trace_owner_join_api_web42 as resolver

if __name__=='__main__':
    register.run(Path(__file__),resolver,register.BASE/'PG9522-api-web42-source-join-v1',
      'PG9510-bootstrap17-source-join-v1/manifest.json','7f314d491c7ff05eabf7464cd3f42efb313cfbb5e8c499b5c49b316f77f3c650',
      'PG9520-api-web42-source-post-v1/manifest.json','4f8bc5b38d2aaac3af21860bf789753f35138de39a32ae72b96c140e5852c6a9',42,1769)
