"""Register fixed API transaction/JMS20 source labels; all actual runtime conditions remain held."""
from pathlib import Path
import explicit_primary_source_registration as register
import trace_owner_join_api_jms20 as resolver

if __name__=='__main__':
    register.run(Path(__file__),resolver,register.BASE/'PG9438-api-jms20-source-join-v1',
      'PG9426-resource33-source-join-v1/manifest.json','91f349d3158c28d4b6da2bfddf9c2ca1b9469de764ebb2d87cb4c7d137f21690',
      'PG9436-api-jms20-source-post-v1/manifest.json','3ef738b8dbb2f759be25e2058257a7396a439e1274e90792094577eb97002614',20,1586)
