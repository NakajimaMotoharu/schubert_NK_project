"""Register7 reviewed shared fixtures; source responsibility only, no native/DB/PT credit."""
from pathlib import Path
import explicit_primary_source_registration as register
import trace_owner_join_shared_fixture7 as resolver

if __name__=='__main__':
    register.run(Path(__file__),resolver,register.BASE/'PG9546-shared-fixture7-source-join-v1',
      'PG9534-fixture-consumer5-source-join-v1/manifest.json','69d5360bb5d7fb9f8e9eef09ca7427ecb24f01acfa3c682a5eb9bc41033a62e8',
      'PG9544-shared-fixture7-source-post-v1/manifest.json','b3fe5741799dfa2d46af261279baf5753bb07f77ba1e60bfa8c7bb3aa66da643',7,1781)
