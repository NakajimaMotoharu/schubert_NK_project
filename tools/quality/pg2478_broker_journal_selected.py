"""Four isolated journal boundary PT; current immutable Main and qualified native only."""
import inspect
import json
import pg2220_root_uid_host_selected as prior
from pyflakes.api import check

SOURCE = 'cdbc07cdf77370d521e64de8b327da7f6752139b'
FILES = ['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/BrokerJournalEvidenceTest.java',
         'tools/quality/vm/050_s1/Pg2478BrokerJournalBoundaryLauncher.java', *prior.FILES[2:]]


def native_input():
    m = json.loads((prior.W / 'pg2474-question-current-native-qualified-v1/manifest.safe.json').read_bytes())
    i = json.loads((prior.W / 'pg2474-question-current-native-qualified-v1/input.safe.json').read_bytes())
    r = m['result']
    if m['actualExit'] != 0 or m['productionSource'] != SOURCE or r['classByteMismatch'] != 0 or r['currentNativeStreams'] != 9 or not r['inspectorLatestClosingOnly'] or not r['inspectorProbeMonotonic']:
        raise ValueError('current qualified latest-only native required')
    files = {str(n) + '.exec': p['sha256'] for n, p in enumerate(i['selected'])
             if not (p['unit'] == 'schubert-nk-inbox-inspector.service' and p['relative'].endswith('.terminal.exec'))}
    if len(files) != 9:
        raise ValueError('nine qualified streams required')
    full = json.loads((prior.W / 'pg2405-question-jdbc-full-qualified-v1/manifest.safe.json').read_bytes())
    if full['actualExit'] != 0 or i['qualifiedFull'] != full['result']:
        raise ValueError('same full authority required')
    return {'files': files, 'manifestSha256': m['manifestSha256']}


def server():
    raw = prior.SERVER.replace('PG2220', 'PG2478').replace('Pg2220RootUidLauncher', 'Pg2478BrokerJournalBoundaryLauncher').replace('source-full-PG2124', 'source-full-PG2404')
    raw = raw.replace('tests1 failures0', 'tests4 failures0').replace("'tests':'1'", "'tests':'4'").replace("len(x.findall('testcase'))==1", "len(x.findall('testcase'))==4").replace("'tests':1", "'tests':4")
    marker = "fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    extra = """native_root=b/'runs/PG2474-native-v1';require(sha(native_root/'manifest.safe.json')==INPUT['native']['manifestSha256'])
native_streams=[]
for n,h in INPUT['native']['files'].items():
 p=native_root/n;require(sha(p)==h);native_streams.append(str(p))
require(len(native_streams)==9)
"""
    if raw.count(marker) != 1:
        raise ValueError('single immutable fixture boundary required')
    raw = raw.replace(marker, extra + marker).replace('*hosts,str(execfile)', '*hosts,*native_streams,str(execfile)').replace('remainingHostOnly', 'remainingSameSourceWithNative')
    raw = raw.replace("require(all(sha(fixtures/n)==h for n,h in fixture_hashes.items()))", "require(all(sha(fixtures/n)==h for n,h in fixture_hashes.items()))\nrequire(all(sha(native_root/n)==h for n,h in INPUT['native']['files'].items()))")
    if check('INPUT={}\n' + raw, '<PG2478 isolated current journal>'):
        raise ValueError('actual namespace required')
    compile(raw, '<PG2478 selected>', 'exec')
    return raw


def main():
    raw = inspect.getsource(prior.main).replace('PG2220', 'PG2478').replace('pg2220', 'pg2478').replace('pg2125-metadata-boundary-full-qualified-v1', 'pg2405-question-jdbc-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    namespace = {**prior.__dict__, 'SOURCE': SOURCE, 'FILES': FILES, 'SLOT': 'pg2478-broker-journal-selected-v1', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<PG2478 immutable transport>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
