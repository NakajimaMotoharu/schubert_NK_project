"""Current Main explicit Caddy parser two-test selected run, no VM operation."""
import inspect
import pg1625_unsupported_ports_selected as engine
from pg1743_root_generation_boundaries_selected import server as root_server
from pg1719_current_bootstrap_sources import SOURCE

SLOT='pg1746-caddy-address-selected-v1'
FILES=['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CaddyAddressBoundaryTest.java','tools/quality/vm/050_s1/Pg1746CaddyAddressLauncher.java','tools/quality/vm/050_s1/NativeCoverage.java','tools/quality/vm/050_s1/NativeCoverageXml471.java']

def server():
    raw=root_server().replace('PG1743','PG1746').replace('Pg1743RootGenerationBoundaryLauncher','Pg1746CaddyAddressLauncher')
    raw=raw.replace('TEST-dev.codex.schubert.nk.batch.platform.RootStartupContextTest.xml','TEST-dev.codex.schubert.nk.batch.file.CaddyPublicConfigurationTest.xml')
    for a,b in [('tests8','tests2'),("=='8'","=='2'"),('==8)','==2)'),("'tests':8","'tests':2")]:raw=raw.replace(a,b)
    marker='coverage={};xml_hashes={}'
    raw=raw.replace(marker,"""rootq=b/'runs/PG1745-selected-qualification-v1/manifest.safe.json'
require(sha(rootq)=='acaa8faa41a41efe9b9cfe4dab4e226d74c0854ad30c1132adf8f53aab4d2360')
rq=json.loads(rootq.read_bytes());require(rq['source']==INPUT['productionSource']and rq['results']['1743']['tests']==8)
re=b/'runs/PG1743-selected-v1/selected.exec';require(sha(re)==rq['results']['1743']['originalExecSha256']);streams.append(str(re))
coverage={};xml_hashes={}""")
    compile(raw,'<two Caddy parser boundaries>','exec');return raw

def main():
    raw=inspect.getsource(engine.main).replace('PG1625','PG1746').replace('pg1625','pg1746')
    raw=raw.replace('pg1618-current-ordinary-native-qualified-v3','pg1735-current-bootstrap-native-qualified-v1').replace('pg1624-same-source-native-campaign-v1','pg1735-current-bootstrap-native-qualified-v1')
    ns={**engine.__dict__,'FILES':FILES,'SLOT':SLOT,'SERVER':server(),'SOURCE':SOURCE}
    exec(compile(raw,'<new-only two parser transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
