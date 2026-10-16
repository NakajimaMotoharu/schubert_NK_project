"""One Test-only integration: old3714 retained plus two independent Session contracts."""
import inspect
import json
import subprocess
import pg3734_hygiene_full_six as previous
from pg3274_header_group_full_six import rebase

ROOT, W, SOURCE = previous.ROOT, previous.W, previous.SOURCE
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSessionTest.java'
EXPECTED = {**previous.EXPECTED, 'batch': (1307, 174, 568)}
NEW_CASES = [('dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest', n) for n in [
    'mdb3920001RetainedRequestTimeBoundariesPreserveActualRowsAndOwnedLock',
    'mdb3924001DifferentFailureMetricsCannotMintCanonicalFailedPairSnapshot']]
require = previous.require
BASIS = '3714 retained plus independent Session retained-request boundary and failed-pair authority tests;545suite1643Main; Test-only group'
TRIGGER = 'PT-MDB-3920-001/PT-MDB-3924-001 completed independent boundary group; required one fresh Test-only integration; no Main/VM/duplicate run'


def validate(snapshot):
    full = json.loads((W / 'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes())
    selected = json.loads((W / 'pg3926-current-failed-pair-boundary-v1/manifest.safe.json').read_bytes())
    require(full['actualExit'] == selected['actualExit'] == selected['result']['actualExit'] == 0, 'both actual old full and new65 selected success')
    require(full['result']['productionSource'] == selected['productionSource'] == SOURCE and full['result']['tests'] == 3714 and selected['result']['tests'] == 65, 'same current source and genuine counts')
    changed = subprocess.check_output(['git', 'diff', '--name-only', full['result']['sourceSnapshot'], snapshot, '--', *previous.previous.base.SCOPE], cwd=ROOT, text=True).splitlines()
    require(changed == [TEST], 'one Test-only group; no Main/config/resource/build changes')
    expected = subprocess.check_output(['git', 'show', selected['testSource'] + ':' + TEST], cwd=ROOT)
    require((ROOT / TEST).read_bytes() == expected and expected.decode().count('@Test\n') == 65, 'actual selected-tested immutable65 bytes')
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'clean fixed operator')


def server_source(head, digest):
    h, d = 'a2' * 20, 'b3' * 32
    return rebase(previous.server_source(h, d), 'PG3734', 'PG3928', 3714, 3716, {h: head, d: digest})


def operator_source():
    raw = inspect.getsource(previous.main).replace('PG3734', 'PG3928').replace('pg3734', 'pg3928').replace('3714', '3716')
    for old, new in [
        ('3712 retained plus exact two independent Root inode value/ACL boundary cases;545suite1643Main; batched semantic-proof source hygiene', BASIS),
        ('BUG1312 Test boundary plus BUG1313/1317/1320 batched cross-module Main hygiene; required one fresh whole, old4856 native not candidate credit', TRIGGER)]:
        require(raw.count(old) == 1, 'exact human-readable trigger boundary required')
        raw = raw.replace(old, new)
    compile(raw, '<whole operator with actual two-boundary trigger>', 'exec')
    return raw


def main():
    raw = operator_source()
    namespace = {**previous.__dict__, 'validate': validate, 'server_source': server_source}
    exec(compile(raw, '<one necessary Test-group3716 integration>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
