"""One necessary Test-stream correction whole3702/independent/native28 integration.

Production a9 and test counts are unchanged. Digest-safe existing builders and
all original member/source/CRC gates are retained; no VM or operation replay.
"""
import argparse
import hashlib
import inspect
import json
import subprocess

from pyflakes.api import check

import pg2798_jdbc_null_fixed_full_six as engine
import pg3302_directional_group_full_six as prior_whole
import pg3304_directional_group_full_qualified as prior_independent
import pg3306_directional_group_native_rejoin as prior_native
from pg3274_header_group_full_six import rebase

ROOT, SOURCE, W = prior_whole.ROOT, prior_whole.SOURCE, prior_whole.W
TEST = 'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/StorageRootInspectionTest.java'


def require(value, message):
    if not value:
        raise ValueError(message)


def validate(snapshot):
    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT)
    old = json.loads((W / 'pg3304-directional-group-full-qualified-v1/manifest.safe.json').read_bytes())
    related_path = W / 'pg3326-storage-stream-after-v2'
    related = json.loads((related_path / 'manifest.safe.json').read_bytes())
    require(old['actualExit'] == 0 and old['result']['tests'] == 3702 and old['result']['productionSource'] == SOURCE, 'actual previous3702 required')
    changed = set(git('diff', '--name-only', old['result']['sourceSnapshot'], snapshot, '--', *engine.SCOPE).decode().splitlines())
    require(changed == {TEST}, 'exact one Test-only ownership correction; no Main/resource/settings change')
    r = related['result']
    require(related['actualExit'] == r['actualExit'] == r['mavenExit'] == r['staticIssues'] == 0
            and r['source'] == SOURCE and r['counts'] == {'tests': 163, 'suites': 23, 'failures': 0, 'errors': 0, 'skipped': 0}
            and r['mainClasses'] == 74 and r['allMainResourcesDebugSameBytes'] is True
            and r['childUmask'] == '0027', 'actual corrected Storage163/all member identity required')
    require(all(r['coverage'][k]['missed'] == 0 for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']), 'related Storage four100 required')
    require(hashlib.sha256((related_path / 'regression.private.py').read_bytes()).hexdigest() == related['payloadSha256'], 'fixed actual related payload required')
    actual = git('show', snapshot + ':' + TEST)
    require(hashlib.sha256(actual).hexdigest() == r['testSha256']
            and actual == git('show', related['testSource'] + ':' + TEST), 'same actually tested correction required')
    require(actual.decode().count('@Test\n') == 3
            and git('show', old['result']['sourceSnapshot'] + ':' + TEST).decode().count('@Test\n') == 3, 'test count unchanged, not arithmetic addition')
    before = json.loads((W / 'pg3326-storage-stream-before-v1/manifest.safe.json').read_bytes())
    require(before['actualExit'] == 0 and before['result']['mavenExit'] == 1
            and before['result']['counts'] == {'tests': 3, 'suites': 1, 'failures': 1, 'errors': 0, 'skipped': 0}, 'original exact FD0to2 rejection retained required')


def server_source(head, digest):
    return rebase(prior_whole.server_source(head, digest), 'PG3302', 'PG3330', 3702, 3702)


def independent_server():
    result = rebase(prior_independent.server(), 'PG3302', 'PG3330', 3702, 3702)
    require(check(result, '<independent stream3702>') == 0, 'complete independent namespace')
    return result


def native_build(*args):
    result = rebase(prior_native.build(*args), 'PG3302', 'PG3330', 3702, 3702)
    result = result.replace('PG3306-native-join-v1', 'PG3334-native-join-v1')
    require(check(result, '<stream3702 sealed28>') == 0, 'complete native namespace')
    return result


def whole():
    raw = inspect.getsource(engine.main).replace('PG2798', 'PG3330').replace('pg2798', 'pg3330').replace('3680', '3702')
    raw = raw.replace('3673 retained plus five independently real-DB Session methods and two owner-admission methods; changed JDBC Main;542suite1643',
                      '3702 retained, one Test file lexical stream close and independent fixture FD postcondition; Main a9 unchanged;542suite1643')
    raw = raw.replace('BUG1251/YKT1017 changed JDBC null-resource Main and seven grouped tests require one fresh all-source/static regression; Source042 native not portable',
                      'BUG1289/YKT1055 actual FD leak rejected before, related corrected Storage163/23 four100; one necessary whole integration; no VM/Root/sign/deploy replay')
    namespace = {**engine.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server_source': server_source}
    exec(compile(raw, '<one stream3702 transport>', 'exec'), namespace)
    return namespace['main']()


def qualify():
    raw = inspect.getsource(prior_independent.engine.main).replace('pg2800-jdbc-null-fixed-full-qualified-v1', 'pg3332-stream-group-full-qualified-v1').replace('pg2798-server-six-v1', 'pg3330-server-six-v1').replace('PG2798', 'PG3330')
    namespace = {**prior_independent.engine.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server': independent_server}
    exec(compile(raw, '<independent stream3702 transport>', 'exec'), namespace)
    return namespace['main']()


def native():
    raw = inspect.getsource(prior_native.previous.main).replace('pg3276-header-group-full-qualified-v1', 'pg3332-stream-group-full-qualified-v1').replace('pg3278-header-group-native-qualified-v1', 'pg3334-stream-group-native-qualified-v1')
    namespace = {**prior_native.previous.__dict__, 'SOURCE': SOURCE, 'validate': validate,
                 'build': native_build, 'public_summary': prior_native.public_summary}
    exec(compile(raw, '<stream3702/native28 transport>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['whole', 'qualify', 'native'])
    raise SystemExit({'whole': whole, 'qualify': qualify, 'native': native}[parser.parse_args().action]())
