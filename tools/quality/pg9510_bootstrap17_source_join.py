"""Register17 exact Bootstrap/shared checkpoint labels without any runtime/PT credit."""
from pathlib import Path
import explicit_primary_source_registration as register
import trace_owner_join_bootstrap17 as resolver

if __name__=='__main__':
    register.run(Path(__file__),resolver,register.BASE/'PG9510-bootstrap17-source-join-v1',
      'PG9498-batch-file37-source-join-v1/manifest.json','96770fbedea32222e1492af2b158cfa9055622a31d15486c4ac7b4033723a1a4',
      'PG9508-bootstrap17-source-post-v1/manifest.json','4ea772b5dee1158fb6290b8bdeb422379651edd67ff4377c589bdef39e922445',17,1727)
