"""Fresh four existing API rejection contracts with isolated child/parent exec.

No Production/test mutation. Qualified Main/fixture bytes are reused, never
earlier pass results. Every child is a separate natural JVM shutdown session.
"""
import inspect
import pg1628_unsupported_ports_selected as prior


def server():
    raw=prior.SERVER.replace('PG1628','PG1629').replace('Pg1628SelectedLauncher','Pg1629ApiMainLauncher')
    raw=raw.replace("fixtures=source/'src/schubert-nk-batch/target/test-classes'", "fixtures=source/'src/schubert-nk-api/target/test-classes'")
    raw=raw.replace('dev/codex/schubert/nk/batch/file/BackupDatabaseWorkerTest$Fixture.class','dev/codex/schubert/nk/api/bootstrap/ApiProcessMainTest.class')
    raw=raw.replace("cp=':'.join(jars+[str(fixtures)]+libraries)", """baseline_xml=source/'src/schubert-nk-api/target/surefire-reports/TEST-dev.codex.schubert.nk.api.bootstrap.ApiProcessMainTest.xml'
baseline_xml_hash=sha(baseline_xml)
props={v.attrib['name']:v.attrib['value']for v in ET.parse(baseline_xml).getroot().findall('properties/property')}
api_library_hashes={}
for name in props['surefire.test.class.path'].split(':'):
 p=Path(name)
 if p.is_relative_to(repo):
  require(p.is_file() and p.suffix=='.jar');api_library_hashes[str(p.relative_to(repo))]=sha(p)
  if str(p)not in libraries:libraries.append(str(p))
cp=':'.join(jars+[str(fixtures)]+libraries)""")
    raw=raw.replace(',append=false',',append=true')
    raw=raw.replace('tests8','tests4').replace("=='8'","=='4'").replace('==8)','==4)').replace("'tests':8","'tests':4")
    marker="coverage={};xml_hashes={}"
    raw=raw.replace(marker,"""old=b/'runs/PG1628-selected-v1';require(sha(old/'manifest.safe.json')=='19e45bebc6a91ae26655578e298dbd917b0af66277a0cd9a008035aea5ecacc6')
old_manifest=json.loads((old/'manifest.safe.json').read_bytes());require(old_manifest['productionSource']==INPUT['productionSource'] and old_manifest['actualExit']==0 and old_manifest['tests']==8 and old_manifest['mainJarHashes']==full['jarHashes'] and sha(old/'selected.exec')==old_manifest['execSha256'])
streams.append(str(old/'selected.exec'))
coverage={};xml_hashes={}""")
    raw=raw.replace("result={'actualExit':0", "require(sha(baseline_xml)==baseline_xml_hash and all(sha(repo/n)==h for n,h in api_library_hashes.items()))\nresult={'apiLibraryHashes':api_library_hashes,'apiBaselineClasspathXmlSha256':baseline_xml_hash,'childAndParentAppendAtNaturalShutdown':True,'actualExit':0")
    compile(raw,'<actual isolated API four suite>','exec')
    return raw


def main():
    names=['tools/quality/vm/050_s1/Pg1629ApiMainLauncher.java','tools/quality/vm/050_s1/NativeCoverage.java','tools/quality/vm/050_s1/NativeCoverageXml471.java']
    ns={**prior.__dict__,'FILES':names,'SLOT':'pg1629-api-main-selected-v1','SERVER':server()}
    exec(compile(inspect.getsource(prior.main).replace('PG1628','PG1629').replace('pg1628','pg1629'),'<fresh isolated API dispatch>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
