"""Current Main generation4 with literal kernel fixtures; no VM management."""
import inspect
import pg1737_successful_backup_projection_selected as prior

SLOT='pg1741-root-generation-selected-v1'
FILES=['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/RootGenerationCounterexampleTest.java',
 'tools/quality/vm/050_s1/Pg1741RootGenerationLauncher.java',
 'tools/quality/vm/050_s1/NativeCoverage.java','tools/quality/vm/050_s1/NativeCoverageXml471.java']

def server():
    raw=prior.server().replace('PG1737','PG1741').replace('Pg1737SuccessfulProjectionLauncher','Pg1741RootGenerationLauncher')
    raw=raw.replace('TEST-dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest.xml','TEST-dev.codex.schubert.nk.batch.platform.RootStartupContextTest.xml')
    for a,b in [('tests6','tests4'),("=='6'","=='4'"),('==6)','==4)'),("'tests':6","'tests':4")]:raw=raw.replace(a,b)
    marker='coverage={};xml_hashes={}'
    raw=raw.replace(marker,"""projection_qualification=b/'runs/PG1740-selected-qualification-v1/manifest.safe.json'
require(sha(projection_qualification)=='a346f4429117583c9a9550e5c5a3c919259c2f276681c317a0b57fbb2e0eb27a')
pq=json.loads(projection_qualification.read_bytes());require(pq['source']==INPUT['productionSource']and pq['results']['1739']['tests']==7)
projection=b/'runs/PG1739-selected-v1';require(sha(projection/'selected.exec')==pq['results']['1739']['originalExecSha256'])
streams.append(str(projection/'selected.exec'))
coverage={};xml_hashes={}""")
    compile(raw,'<four literal kernel generation contracts>','exec');return raw

def main():
    raw=inspect.getsource(prior.main).replace('PG1737','PG1741').replace('pg1737','pg1741')
    ns={**prior.__dict__,'FILES':FILES,'SLOT':SLOT,'server':server}
    exec(compile(raw,'<isolated kernel generation4 transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
