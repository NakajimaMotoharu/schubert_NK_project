"""Publication entry guards only, fixed current full/native; no actual startup/SQL capability."""
import inspect
import json
from pyflakes.api import check
import pg2220_root_uid_host_selected as transport
from pg2674_operation_publication_sources import production

SOURCE=production()
FILES=['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwnerAdmissionTest.java',
       'tools/quality/vm/050_s1/Pg2776StartupOwnerAdmissionLauncher.java',*transport.FILES[2:]]


def native_input():
    receipt=json.loads((transport.W/'pg2774-db-contract-native-qualified-v1/manifest.safe.json').read_bytes())
    full=json.loads((transport.W/'pg2772-db-contract-full-qualified-v1/manifest.safe.json').read_bytes())
    original=json.loads((transport.W/'pg2722-operation-native-qualified-v1/input.safe.json').read_bytes())
    r=receipt['result']
    if any(type(v.get('actualExit'))is not int or v['actualExit']!=0 for v in [receipt,full]):raise ValueError('actual full/current native required')
    if receipt.get('productionSource')!=SOURCE or original.get('productionSource')!=SOURCE or r['classByteMismatch']!=0 or r['qualified2770Tests']!=3673 or r['all1643MainMembersIdentical']!=1643 or r['oldNativeImported']is not False or full['result']['tests']!=3673:
        raise ValueError('actual whole-byte current full/ownnative required')
    files={str(i)+'.exec':v['sha256']for i,v in enumerate(original['selected'])if not(v['unit']=='schubert-nk-inbox-inspector.service'and v['relative'].endswith('.terminal.exec'))}
    if len(files)!=9:raise ValueError('latest closing only nine streams required')
    return {'manifestSha256':receipt['manifestSha256'],'files':files}


def server():
    raw=transport.SERVER.replace('PG2220','PG2776').replace('Pg2220RootUidLauncher','Pg2776StartupOwnerAdmissionLauncher').replace('source-full-PG2124','source-full-PG2770')
    for a,b in [('tests1 failures0','tests2 failures0'),("'tests':'1'","'tests':'2'"),("len(x.findall('testcase'))==1","len(x.findall('testcase'))==2"),("'tests':1","'tests':2")]:
        if a not in raw:raise ValueError('exact two actual JUnit requirement boundary')
        raw=raw.replace(a,b)
    marker="fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    native="""native_root=b/'runs/PG2774-native-v1';require(sha(native_root/'manifest.safe.json')==INPUT['native']['manifestSha256'])
native_streams=[]
for name,h in INPUT['native']['files'].items():
 p=native_root/name;require(sha(p)==h);native_streams.append(str(p))
require(len(native_streams)==9)
"""
    if raw.count(marker)!=1:raise ValueError('one native/fixture immutable boundary required')
    raw=raw.replace(marker,native+marker).replace('*hosts,str(execfile)','*hosts,*native_streams,str(execfile)').replace('remainingHostOnly','remainingSameSourceWithNative')
    marker="require(all(sha(fixtures/n)==h for n,h in fixture_hashes.items()))"
    if raw.count(marker)!=1:raise ValueError('one unchanged fixture post required')
    raw=raw.replace(marker,marker+"\nrequire(all(sha(native_root/n)==h for n,h in INPUT['native']['files'].items()))")
    if check('INPUT={}\n'+raw,'<owner admission complete namespace>'):raise ValueError('whole namespace required')
    compile(raw,'<publication entry guard only>','exec');return raw


def transport_body():
    raw=inspect.getsource(transport.main).replace('PG2220','PG2776').replace('pg2220','pg2776').replace(
        'pg2125-metadata-boundary-full-qualified-v1','pg2772-db-contract-full-qualified-v1')
    raw=raw.replace(",'libraries':libs}",",'libraries':libs,'native':native_input()}")
    if raw.count('PG2776-selected-v1')!=5:raise ValueError('completed one new-only transport role required')
    compile(raw,'<owner selected complete transport>','exec');return raw


def main():
    ns={**transport.__dict__,'SOURCE':SOURCE,'FILES':FILES,'SLOT':'pg2776-startup-owner-admission-selected-v1','SERVER':server(),'native_input':native_input}
    exec(compile(transport_body(),'<owner admission fixed input>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
