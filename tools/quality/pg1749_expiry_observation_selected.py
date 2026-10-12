"""Current Main literal Expiry observation matrices, no actual DB/VM owner."""
import inspect
import pg1625_unsupported_ports_selected as engine
from pg1746_caddy_address_selected import server as caddy_server
from pg1719_current_bootstrap_sources import SOURCE

SLOT='pg1749-expiry-observation-selected-v1'
FILES=['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningExpiryObservationInvariantTest.java','tools/quality/vm/050_s1/Pg1749ExpiryObservationLauncher.java','tools/quality/vm/050_s1/NativeCoverage.java','tools/quality/vm/050_s1/NativeCoverageXml471.java']

def server():
    raw=caddy_server().replace('PG1746','PG1749').replace('Pg1746CaddyAddressLauncher','Pg1749ExpiryObservationLauncher')
    raw=raw.replace('TEST-dev.codex.schubert.nk.batch.file.CaddyPublicConfigurationTest.xml','TEST-dev.codex.schubert.nk.batch.repository.MorningExpirySessionTest.xml')
    for a,b in [('tests2','tests4'),("=='2'","=='4'"),('==2)','==4)'),("'tests':2","'tests':4")]:raw=raw.replace(a,b)
    # Only current run number strings above change; previous qualified Root stream must remain1743.
    marker='coverage={};xml_hashes={}'
    raw=raw.replace(marker,"""cq=b/'runs/PG1747-selected-qualification-v1/manifest.safe.json'
require(sha(cq)=='d28c0718dda236f3bb1507562a4d26997d148d484d8161d2a4b005312fb44cb3')
qc=json.loads(cq.read_bytes());require(qc['source']==INPUT['productionSource']and qc['results']['1746']['tests']==2)
ce=b/'runs/PG1746-selected-v1/selected.exec';require(sha(ce)==qc['results']['1746']['originalExecSha256']);streams.append(str(ce))
coverage={};xml_hashes={}""")
    compile(raw,'<four Expiry data matrices>','exec');return raw

def main():
    raw=inspect.getsource(engine.main).replace('PG1625','PG1749').replace('pg1625','pg1749')
    raw=raw.replace('pg1618-current-ordinary-native-qualified-v3','pg1735-current-bootstrap-native-qualified-v1').replace('pg1624-same-source-native-campaign-v1','pg1735-current-bootstrap-native-qualified-v1')
    ns={**engine.__dict__,'FILES':FILES,'SLOT':SLOT,'SERVER':server(),'SOURCE':SOURCE}
    exec(compile(raw,'<new-only four Expiry data transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
