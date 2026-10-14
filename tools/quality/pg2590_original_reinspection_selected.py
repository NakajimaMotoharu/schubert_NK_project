"""Actual isolated original-row drift and stale eligibility, current immutable Main only."""
import inspect
import json
from pathlib import Path
from pyflakes.api import check
import pg2588_retention_eligibility_selected as previous

FILES = [previous.FILES[0], 'tools/quality/vm/050_s1/Pg2590OriginalReinspectionLauncher.java', *previous.FILES[2:]]


def native_input():
    value = previous.native_input()
    proof = json.loads(Path('evidence/01_PT/018_NK-OPS-001/evidence/strict-current-reference/retention-eligibility-manifest.json').read_bytes())
    if (type(proof.get('actualExit')) is not int or proof['actualExit'] != 0
            or proof.get('source') != previous.SOURCE or proof.get('tests') != 1
            or proof.get('FESAbortedNotRun') != 0 or proof.get('classByteMismatch') != 0):
        raise ValueError('actual same Main retention projection required')
    value['eligibilityServerManifestSha256'] = proof['manifestSha256']
    return value


def server():
    raw = previous.server().replace('PG2588', 'PG2590').replace(
        'Pg2588RetentionEligibilityLauncher', 'Pg2590OriginalReinspectionLauncher')
    marker = "fixtures=source/'src/schubert-nk-batch/target/test-classes'"
    if raw.count(marker) != 1:
        raise ValueError('one immutable fixture boundary required')
    extra = """prior_root=b/'runs/PG2588-selected-v1'
require(sha(prior_root/'manifest.safe.json')==INPUT['native']['eligibilityServerManifestSha256'])
prior=json.loads((prior_root/'manifest.safe.json').read_bytes())
require(prior['actualExit']==0 and prior['source']==INPUT['source'] and prior['input']['full']['jarHashes']==INPUT['full']['jarHashes'])
prior_exec=prior_root/'selected.exec';require(sha(prior_exec)==prior['execSha256'])
"""
    raw = raw.replace('PG2590-selected-v1', 'PG2590-selected-v2')
    raw = raw.replace(marker, extra + marker).replace('*hosts,*native_streams,str(execfile)',
        '*hosts,*native_streams,str(prior_exec),str(execfile)')
    if check('INPUT={}\n' + raw, '<current original reinspect namespace>'):
        raise ValueError('whole namespace required')
    compile(raw, '<current original reinspect selected>', 'exec')
    return raw


def main():
    transport = previous.transport
    raw = inspect.getsource(transport.main).replace('PG2220', 'PG2590').replace(
        'pg2220', 'pg2590').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2579-current-jdbc-group-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    ns = {**transport.__dict__, 'SOURCE': previous.SOURCE, 'FILES': FILES,
          'SLOT': 'pg2590-original-reinspection-selected-v2', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fixed original reinspection transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
