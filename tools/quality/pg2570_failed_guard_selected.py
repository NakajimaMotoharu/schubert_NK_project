"""Fresh isolated final JDBC guards, same frozen Main/current nine and prior selected CRC."""
import hashlib
import inspect
import json
from pathlib import Path
from pyflakes.api import check
import pg2568_abandoned_pair_selected as previous

FILES = [previous.FILES[0], 'tools/quality/vm/050_s1/Pg2570FailedGuardLauncher.java', *previous.FILES[2:]]


def native_input():
    value = previous.native_input()
    proof = json.loads(Path('evidence/01_PT/018_NK-OPS-001/evidence/strict-current-reference/abandoned-pair-manifest-v2.json').read_bytes())
    if (type(proof.get('actualExit')) is not int or proof['actualExit'] != 0
            or proof.get('source') != previous.SOURCE or proof.get('tests') != 1
            or proof.get('FESAbortedNotRun') != 0 or proof.get('classByteMismatch') != 0):
        raise ValueError('actual same Main previous selected proof required')
    private = previous.previous.prior.W / 'pg2568-abandoned-pair-selected-v2/selected.private.py'
    if hashlib.sha256(private.read_bytes()).hexdigest() != proof['payloadSha256']:
        raise ValueError('actual selected input digest required')
    value['priorServerManifestSha256'] = proof['manifestSha256']
    return value


def server():
    raw = previous.server().replace('PG2568-selected-v2', 'PG2570-selected-v1').replace(
        'PG2568', 'PG2570').replace('Pg2568AbandonedPairLauncher', 'Pg2570FailedGuardLauncher')
    marker = "fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    if raw.count(marker) != 1:
        raise ValueError('one fixed fixture boundary required')
    extra = """prior_root=b/'runs/PG2568-selected-v2'
require(sha(prior_root/'manifest.safe.json')==INPUT['native']['priorServerManifestSha256'])
prior=json.loads((prior_root/'manifest.safe.json').read_bytes())
require(prior['actualExit']==0 and prior['source']==INPUT['source'] and prior['input']['full']['jarHashes']==INPUT['full']['jarHashes'])
prior_exec=prior_root/'selected.exec';require(sha(prior_exec)==prior['execSha256'])
"""
    raw = raw.replace(marker, extra + marker).replace('*hosts,*native_streams,str(execfile)',
        '*hosts,*native_streams,str(prior_exec),str(execfile)')
    raw = raw.replace("'fixturesUnchanged':True", "'fixturesUnchanged':True,'priorSelectedExecSha256':sha(prior_exec)")
    if check('INPUT={}\n' + raw, '<actual final guards current whole namespace>'):
        raise ValueError('whole selected server namespace required')
    compile(raw, '<fresh final guards>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.previous.prior.main).replace('PG2220', 'PG2570').replace(
        'pg2220', 'pg2570').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2511-strict-reference-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    ns = {**previous.previous.prior.__dict__, 'SOURCE': previous.SOURCE, 'FILES': FILES,
          'SLOT': 'pg2570-failed-guard-selected-v1', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fresh immutable final guard transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
