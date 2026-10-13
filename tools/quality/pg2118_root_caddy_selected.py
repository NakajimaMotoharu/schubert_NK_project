"""Batched Root truth-table + Caddy regression, isolated dependency/cache contracts retained."""
import inspect
import pg2112_caddy_metadata_selected as transport
from pg2116_caddy_metadata_selected_v3 import server as previous

def server():
    raw=previous().replace('PG2116','PG2118')
    raw=raw.replace('-Dtest=CaddyPublicMetadataTest,CaddyPublicConfigurationTest,CaddyPublicCaMetadataTest,CaddyAddressBoundaryTest', '-Dtest=CaddyPublicMetadataTest,CaddyPublicConfigurationTest,CaddyPublicCaMetadataTest,CaddyAddressBoundaryTest,RootGenerationTruthTableTest,RootStartupContextTest')
    old="set(counts)=={'dev.codex.schubert.nk.batch.file.'+n for n in ['CaddyPublicMetadataTest','CaddyPublicConfigurationTest','CaddyPublicCaMetadataTest','CaddyAddressBoundaryTest']}"
    new=old+".union({'dev.codex.schubert.nk.batch.platform.'+n for n in ['RootGenerationTruthTableTest','RootStartupContextTest']})"
    if raw.count(old)!=1:raise ValueError('one exact selected suite set required')
    raw=raw.replace(old,new)
    marker="require(counts['dev.codex.schubert.nk.batch.file.CaddyPublicMetadataTest']=={'tests':4,'failures':0,'errors':0,'skipped':0})"
    raw=raw.replace(marker,marker+"\nrequire(counts['dev.codex.schubert.nk.batch.platform.RootGenerationTruthTableTest']=={'tests':1,'failures':0,'errors':0,'skipped':0})")
    compile(raw,'<Root truth table and Caddy mandatory selection>','exec');return raw

def main():
    raw=inspect.getsource(transport.main).replace('PG2112','PG2118').replace('pg2112','pg2118')
    ns={**transport.__dict__,'SERVER':server()}
    exec(compile(raw,'<new-only Root-Caddy isolated entry>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
