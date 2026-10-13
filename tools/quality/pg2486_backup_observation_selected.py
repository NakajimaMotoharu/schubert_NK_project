"""Real isolated PostgreSQL pair boundaries with immutable current Main and native."""
import hashlib
import inspect
import json
from pathlib import Path
import pg2292_morning_guard_selected as prior
from pg2478_broker_journal_selected import SOURCE, native_input as current_native
from pyflakes.api import check

FILES = [prior.FILES[0], 'tools/quality/vm/050_s1/Pg2486BackupObservationLauncher.java', *prior.FILES[2:]]


def native_input():
    value = current_native()
    path = Path('evidence/01_PT/018_NK-OPS-001/evidence/current-broker-journal-boundaries/manifest-v4.json')
    broker = json.loads(path.read_bytes())
    actual_hash = hashlib.sha256(Path('src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/BrokerJournalEvidenceTest.java').read_bytes()).hexdigest()
    if broker['actualExit'] != 0 or broker['source'] != SOURCE or broker['tests'] != 4 or broker['classByteMismatch'] != 0 or actual_hash != broker['inputFiles']['BrokerJournalEvidenceTest.java']:
        raise ValueError('unchanged independently qualified Broker test source required')
    value['brokerSelectedExecSha256'] = broker['execSha256']
    return value


def server():
    raw = prior.server().replace('PG2292', 'PG2486').replace('Pg2292MorningGuardLauncher', 'Pg2486BackupObservationLauncher').replace('source-full-PG2228', 'source-full-PG2404').replace('PG2284-native-v1', 'PG2474-native-v1')
    raw = raw.replace('tests2 failures0', 'tests4 failures0').replace("'tests':'2'", "'tests':'4'").replace("len(x.findall('testcase'))==2", "len(x.findall('testcase'))==4").replace("'tests':2", "'tests':4")
    raw = raw.replace('PG2486-selected-v1', 'PG2486-selected-v2')
    marker = "fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    extra = """broker_selected=b/'runs/PG2478-selected-v4/selected.exec';require(sha(broker_selected)==INPUT['native']['brokerSelectedExecSha256'])
"""
    if raw.count(marker) != 1:
        raise ValueError('one frozen fixture boundary required')
    raw = raw.replace(marker, extra + marker).replace('*hosts,*native_streams,str(execfile)', '*hosts,*native_streams,str(broker_selected),str(execfile)')
    raw = raw.replace("require(all(sha(fixtures/n)==h for n,h in fixture_hashes.items()))", "require(all(sha(fixtures/n)==h for n,h in fixture_hashes.items()))\nrequire(sha(broker_selected)==INPUT['native']['brokerSelectedExecSha256'])")
    if check('INPUT={}\n' + raw, '<PG2486 independent current pair>'):
        raise ValueError('actual whole selected namespace required')
    compile(raw, '<PG2486 pair selected>', 'exec')
    return raw


def main():
    raw = inspect.getsource(prior.prior.main).replace('PG2220', 'PG2486').replace('pg2220', 'pg2486').replace('pg2125-metadata-boundary-full-qualified-v1', 'pg2405-question-jdbc-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    raw = raw.replace('PG2486-selected-v1', 'PG2486-selected-v2')
    namespace = {**prior.prior.__dict__, 'SOURCE': SOURCE, 'FILES': FILES, 'SLOT': 'pg2486-backup-pair-selected-v2', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<PG2486 isolated selected transport>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
