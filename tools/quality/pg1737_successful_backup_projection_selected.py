"""Current Main isolated SQL projection6; literal rows, no VM or actual DB."""
import inspect
import pg1625_unsupported_ports_selected as engine
from pg1719_current_bootstrap_sources import SOURCE

SLOT='pg1737-successful-backup-projection-selected-v1'
FILES=[
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSessionTest.java',
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningSuccessfulBackupProjectionTest.java',
 'tools/quality/vm/050_s1/Pg1737SuccessfulProjectionLauncher.java',
 'tools/quality/vm/050_s1/NativeCoverage.java','tools/quality/vm/050_s1/NativeCoverageXml471.java']

def server():
    raw=engine.SERVER.replace('PG1625','PG1737').replace('Pg1625SelectedLauncher','Pg1737SuccessfulProjectionLauncher').replace('PG1532','PG1633').replace('PG1624-native-campaign-v1','PG1735-native-v1').replace('PG1618-native-v1','PG1735-native-v1')
    for a,b in [('tests3','tests6'),("=='3'","=='6'"),('==3)','==6)'),("'tests':3","'tests':6")]:raw=raw.replace(a,b)
    marker="cp=':'.join(jars+[str(fixtures)]+libraries)"
    if raw.count(marker)!=1:raise ValueError('one fixture compiler dependency boundary required')
    raw=raw.replace(marker,"""baseline_xml=source/'src/schubert-nk-batch/target/surefire-reports/TEST-dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest.xml'
baseline_xml_hash=sha(baseline_xml)
props={v.attrib['name']:v.attrib['value']for v in ET.parse(baseline_xml).getroot().findall('properties/property')}
fixture_libraries={}
for name in props['surefire.test.class.path'].split(':'):
 p=Path(name)
 if p.is_relative_to(repo):
  require(p.is_file()and p.suffix=='.jar');fixture_libraries[str(p.relative_to(repo))]=sha(p)
  if str(p)not in libraries:libraries.append(str(p))
cp=':'.join(jars+[str(fixtures)]+libraries)""")
    raw=raw.replace("for cohort in ['PG1590-native-v1','PG1735-native-v1'] for i in range(8)", "for cohort in ['PG1735-native-v1'] for i in range(9)")
    marker='coverage={};xml_hashes={}'
    raw=raw.replace(marker,"""api=b/'runs/PG1716-selected-v1';api_qualification=b/'runs/PG1717-selected-qualification-v1/manifest.safe.json'
require(sha(api_qualification)=='dab6f2d5c4c4823da3bf5a1cff3ef4b786e4e72985c84e595b0831d5d90d223c')
aq=json.loads(api_qualification.read_bytes());require(aq['source']==INPUT['productionSource']and sha(api/'selected.exec')==aq['results']['1716']['originalExecSha256'])
streams.append(str(api/'selected.exec'))
require(sha(baseline_xml)==baseline_xml_hash and all(sha(repo/n)==h for n,h in fixture_libraries.items()))
coverage={};xml_hashes={}""")
    compile(raw,'<current Main six independent literal SQL projections>','exec');return raw

def main():
    raw=inspect.getsource(engine.main).replace('PG1625','PG1737').replace('pg1625','pg1737')
    raw=raw.replace('pg1618-current-ordinary-native-qualified-v3','pg1735-current-bootstrap-native-qualified-v1').replace('pg1624-same-source-native-campaign-v1','pg1735-current-bootstrap-native-qualified-v1')
    ns={**engine.__dict__,'FILES':FILES,'SLOT':SLOT,'SERVER':server(),'SOURCE':SOURCE}
    exec(compile(raw,'<current Main six SQL projection transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
