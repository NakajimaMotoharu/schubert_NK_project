"""Isolated real cleanup/expiry handoff permit DB guards; no startup authority fixture."""
import ast
import inspect
import json
from pyflakes.api import check
import pg2594_resume_admission_selected as previous
from pg2600_retention_group_full_six import SOURCE
from pg1446_current_cold_stage import W

FILES = ['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningExpirySessionTest.java',
         'tools/quality/vm/050_s1/Pg2604PermitDatabaseLauncher.java', *previous.FILES[2:]]


def native_input():
    value = previous.native_input()
    receipt = json.loads((W / 'pg2602-retention-group-native-qualified-v1/manifest.safe.json').read_bytes())
    inputs = json.loads((W / 'pg2602-retention-group-native-qualified-v1/input.safe.json').read_bytes())
    full = json.loads((W / 'pg2601-retention-group-full-qualified-v1/manifest.safe.json').read_bytes())
    result = receipt['result']
    if (receipt['actualExit'] != 0 or receipt['productionSource'] != SOURCE
            or full['actualExit'] != 0 or full['result']['tests'] != 3657
            or inputs['qualifiedFull'] != full['result'] or result['classByteMismatch'] != 0
            or result['currentNativeStreams'] != 9 or result['inspectorLatestClosingOnly'] is not True):
        raise ValueError('actual full3657/current latest-nine qualification required')
    value['manifestSha256'] = receipt['manifestSha256']
    value['files'] = {str(i) + '.exec': v['sha256'] for i, v in enumerate(inputs['selected'])
                      if not (v['unit'] == 'schubert-nk-inbox-inspector.service' and v['relative'].endswith('.terminal.exec'))}
    if len(value['files']) != 9:
        raise ValueError('exact current nine required')
    return value


def server():
    # Start with original reinspection body so previous isolated selections need
    # only their own immutable Jar gate, not replacement with new full container hashes.
    raw = previous.previous.previous.server().replace('PG2590-selected-v3', 'PG2604-selected-v1').replace(
        'Pg2590OriginalReinspectionLauncher', 'Pg2604PermitDatabaseLauncher').replace('PG2590', 'PG2604')
    raw = raw.replace('MorningDatabaseSessionTest', 'MorningExpirySessionTest').replace(
        'source-full-PG2578', 'source-full-PG2600').replace('PG2582-native-v1', 'PG2602-native-v1')
    # Main byte equality was proven independently by2602. Reusing prior exec does
    # not permit a mismatching Jar: preserve its own full/Jar SHA inputs explicitly.
    marker="prior['input']['full']['jarHashes']==INPUT['full']['jarHashes']"
    if raw.count(marker) != 1:
        raise ValueError('one retained selected authority gate required')
    prior_input = ast.literal_eval((W / 'pg2588-retention-eligibility-selected-v1/selected.private.py').read_text().splitlines()[0].removeprefix('INPUT='))
    raw = raw.replace(marker, "prior['input']['full']['jarHashes']==" + repr(prior_input['full']['jarHashes']))
    if check('INPUT={}\n' + raw, '<current permit DB namespace>'):
        raise ValueError('whole namespace required')
    compile(raw, '<current permit DB server>', 'exec')
    return raw


def main():
    transport = previous.previous.previous.previous.transport
    raw = inspect.getsource(transport.main).replace('PG2220', 'PG2604').replace(
        'pg2220', 'pg2604').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2601-retention-group-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    ns = {**transport.__dict__, 'SOURCE': SOURCE, 'FILES': FILES,
          'SLOT': 'pg2604-permit-database-selected-v1', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fixed permit DB transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
