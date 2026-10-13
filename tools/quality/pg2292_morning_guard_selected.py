"""Two actual independent PostgreSQL guard PT against frozen current Main JARs."""
import inspect
import json
import pg2220_root_uid_host_selected as prior

FILES=['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSessionTest.java','tools/quality/vm/050_s1/Pg2292MorningGuardLauncher.java','tools/quality/vm/050_s1/NativeCoverage.java','tools/quality/vm/050_s1/NativeCoverageXml471.java']


def native_input():
    value=json.loads((prior.W/'pg2284-current-signed-native-qualified-v1/manifest.safe.json').read_bytes());result=value['result']
    inputs=json.loads((prior.W/'pg2284-current-signed-native-qualified-v1/input.safe.json').read_bytes())
    full=json.loads((prior.W/'pg2236-root-host-integration-full-qualified-v1/manifest.safe.json').read_bytes())['result']
    if value['actualExit']!=0 or value['productionSource']!=prior.SOURCE or result['classByteMismatch']!=0 or result['currentNativeStreams']!=9 or not result['inspectorLatestClosingOnly']or not result['inspectorProbeMonotonic']or inputs['qualifiedFull']['jarHashes']!=full['jarHashes']:
        raise ValueError('actual sameMain current latest-nine qualified parent required')
    files={str(i)+'.exec':p['sha256']for i,p in enumerate(inputs['selected'])if not(p['unit']=='schubert-nk-inbox-inspector.service'and p['relative'].endswith('.terminal.exec'))}
    if len(files)!=9:raise ValueError('nine immutable latest-only streams required')
    return {'manifestSha256':value['manifestSha256'],'files':files}


def server():
    raw=prior.SERVER.replace('PG2220','PG2292').replace('Pg2220RootUidLauncher','Pg2292MorningGuardLauncher').replace('source-full-PG2124','source-full-PG2228')
    raw=raw.replace('tests1 failures0','tests2 failures0').replace("'tests':'1'","'tests':'2'").replace("len(x.findall('testcase'))==1","len(x.findall('testcase'))==2").replace("'tests':1","'tests':2")
    raw=raw.replace("timeout=60,env=env","timeout=150,env=env")
    raw=raw.replace("env={k:v for k,v in os.environ.items()if k not in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS']}","env={k:v for k,v in os.environ.items()if k not in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS']};env['SCHUBERT_PG_ROOT']=str(b/'tools/postgresql18/usr')")
    marker="fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    if raw.count(marker)!=1:raise ValueError('one fixed current fixture/classpath boundary required')
    extra="""fixture_xml=source/'src/schubert-nk-batch/target/surefire-reports/TEST-dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest.xml'
fixture_xml_sha=sha(fixture_xml);existing=ET.parse(fixture_xml).getroot();require(existing.get('failures')=='0'and existing.get('errors')=='0'and existing.get('skipped')=='0')
properties=[n.get('value')for n in existing.findall('properties/property')if n.get('name')=='java.class.path'];require(len(properties)==1 and properties[0])
extra_library_hashes={}
for name in properties[0].split(':'):
 p=Path(name)
 if p.suffix=='.jar'and p.is_relative_to(repo):
  require(p.is_file()and p.resolve().is_relative_to(repo.resolve()))
  extra_library_hashes[str(p.relative_to(repo))]=sha(p)
  if str(p)not in libraries:libraries.append(str(p))
require(any('flyway-core/'in k for k in extra_library_hashes)and any('postgresql/postgresql/'in k for k in extra_library_hashes))
"""
    raw=raw.replace(marker,extra+marker)
    native="""native_root=b/'runs/PG2284-native-v1';require(sha(native_root/'manifest.safe.json')==INPUT['native']['manifestSha256'])
native_streams=[]
for name,h in INPUT['native']['files'].items():
 p=native_root/name;require(sha(p)==h);native_streams.append(str(p))
require(len(native_streams)==9)
"""
    raw=raw.replace(marker,native+marker)
    raw=raw.replace('*hosts,str(execfile)','*hosts,*native_streams,str(execfile)')
    raw=raw.replace('remainingHostOnly','remainingSameSourceWithNative')
    raw=raw.replace("'-Dfile.encoding=UTF-8'","'-Dfile.encoding=UTF-8','-Dnk.pt.repository='+str(source)")
    marker="require(all(sha(fixtures/n)==h for n,h in fixture_hashes.items()))"
    raw=raw.replace(marker,marker+"\nrequire(sha(fixture_xml)==fixture_xml_sha and all(sha(repo/n)==h for n,h in extra_library_hashes.items()))")
    raw=raw.replace(marker,marker+"\nrequire(all(sha(native_root/n)==h for n,h in INPUT['native']['files'].items()))")
    raw=raw.replace("'fixturesUnchanged':True","'fixturesUnchanged':True,'existingSuccessfulXmlSha256':fixture_xml_sha,'extraLibraryHashes':extra_library_hashes,'freshIsolatedPostgres':True")
    from pyflakes.api import check
    if check('INPUT={}\n'+raw,'<actual selected Morning guard server>'):raise ValueError('whole actual namespace required')
    compile(raw,'<selected current Morning guard server>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('PG2220','PG2292').replace('pg2220','pg2292').replace('pg2125-metadata-boundary-full-qualified-v1','pg2236-root-host-integration-full-qualified-v1')
    raw=raw.replace(",'libraries':libs}",",'libraries':libs,'native':native_input()}")
    ns={**prior.__dict__,'FILES':FILES,'SLOT':'pg2292-morning-guard-selected-v1','SERVER':server(),'native_input':native_input}
    exec(compile(raw,'<selected current Morning guard transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
