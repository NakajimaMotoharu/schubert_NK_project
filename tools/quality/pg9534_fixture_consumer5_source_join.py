"""Register5 zero-Main fixtures only after complete consumer proof; no PT/runtime credit."""
from pathlib import Path
import explicit_primary_source_registration as register
import trace_owner_join_fixture_consumer5 as resolver

if __name__=='__main__':
    register.run(Path(__file__),resolver,register.BASE/'PG9534-fixture-consumer5-source-join-v1',
      'PG9522-api-web42-source-join-v1/manifest.json','4f85bf805c3e32dbe668e6374bf6a70cb6fa6c0d93edd1ef4ea99bc30925f927',
      'PG9532-fixture-consumer5-source-post-v1/manifest.json','47eec05441e10730714bc835502afe653dce15881b71557a717050bffab2cd2b',5,1774)
