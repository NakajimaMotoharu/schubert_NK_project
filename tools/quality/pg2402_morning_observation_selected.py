"""PT-MDB2402: real isolated JDBC refusal, frozen Main and two qualified native paths."""
import inspect
import json
import pg2292_morning_guard_selected as prior
from pyflakes.api import check

FILES = [prior.FILES[0], 'tools/quality/vm/050_s1/Pg2402MorningObservationLauncher.java',
         *prior.FILES[2:]]


def native_input():
    joined = json.loads((prior.prior.W / 'pg2390-same-source-native-join-v1/manifest.safe.json').read_bytes())
    if joined['actualExit'] != 0 or joined['productionSource'] != prior.prior.SOURCE or joined['result']['qualifiedNativeStreams'] != 18:
        raise ValueError('same Main qualified two-path technical join required')
    paths = []
    for slot, remote in [('pg2284-current-signed-native-qualified-v1', 'PG2284-native-v1'),
                         ('pg2384-current-resume-native-qualified-v1', 'PG2384-native-v1')]:
        manifest = json.loads((prior.prior.W / slot / 'manifest.safe.json').read_bytes())
        data = json.loads((prior.prior.W / slot / 'input.safe.json').read_bytes())
        if manifest['actualExit'] != 0 or manifest['productionSource'] != prior.prior.SOURCE or len(data['selected']) != 10:
            raise ValueError('two actual same-source qualified native authorities required')
        files = {str(i) + '.exec': p['sha256'] for i, p in enumerate(data['selected'])
                 if not (p['unit'] == 'schubert-nk-inbox-inspector.service' and p['relative'].endswith('.terminal.exec'))}
        if len(files) != 9:
            raise ValueError('latest-only nine streams per qualified activation required')
        paths.append({'root': remote, 'manifestSha256': manifest['manifestSha256'], 'files': files})
    return {'paths': paths, 'technicalJoinManifest': joined['manifestSha256']}


def server():
    raw = prior.server().replace('PG2292', 'PG2402').replace('Pg2292MorningGuardLauncher', 'Pg2402MorningObservationLauncher').replace('source-full-PG2228', 'source-full-PG2300')
    begin = raw.index("native_root=b/'runs/PG2284-native-v1'")
    end = raw.index("fixtures=source/", begin)
    raw = raw[:begin] + """native_streams=[]
for path in INPUT['native']['paths']:
 native_root=b/'runs'/path['root'];require(sha(native_root/'manifest.safe.json')==path['manifestSha256'])
 for name,h in path['files'].items():
  p=native_root/name;require(sha(p)==h);native_streams.append(str(p))
require(len(native_streams)==18)
""" + raw[end:]
    old = "require(all(sha(native_root/n)==h for n,h in INPUT['native']['files'].items()))"
    if raw.count(old) != 1:
        raise ValueError('one immutable native post boundary required')
    raw = raw.replace(old, "require(all(sha(b/'runs'/p['root']/n)==h for p in INPUT['native']['paths'] for n,h in p['files'].items()))")
    if check('INPUT={}\n' + raw, '<real JDBC current two-path selected>'):
        raise ValueError('all actual selected globals required')
    compile(raw, '<real JDBC selected>', 'exec')
    return raw


def main():
    raw = inspect.getsource(prior.prior.main).replace('PG2220', 'PG2402').replace('pg2220', 'pg2402').replace(
        'pg2125-metadata-boundary-full-qualified-v1', 'pg2301-jdbc-host-integration-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    namespace = {**prior.prior.__dict__, 'FILES': FILES, 'SLOT': 'pg2402-morning-observation-selected-v1',
                 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<current two real JDBC observation methods>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
