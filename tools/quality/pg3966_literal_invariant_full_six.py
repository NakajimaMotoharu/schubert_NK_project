"""One new-Main campaign for proven187 constants and independently stable immutable constructor."""
import inspect
import json
import subprocess
import pg3734_hygiene_full_six as previous
from pg3274_header_group_full_six import rebase
from git_source_contract import last_main_source
from pg3962_prior_invariant_selected import MAIN, TEST, METHOD

ROOT, W, require = previous.ROOT, previous.W, previous.require
SOURCE = '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e'
EXPECTED = {**previous.EXPECTED, 'batch': (1308, 174, 568)}
NEW_CASES = [('dev.codex.schubert.nk.batch.platform.ExpiryWorkerRequestTest', METHOD)]
BASIS = '3716 retained plus independent PriorExpiry identity/start boundary;71 literal files plus one immutable constructor;545suite1643Main'
TRIGGER = 'BUG1330/YKT1096 pure187 constants and PG-D421 immutable admission require one72-Main fresh whole; old7fff native not transferable'


def validate(head):
    require(last_main_source(ROOT) == SOURCE, 'exact combined final Main source')
    full = json.loads((W / 'pg3930-current-boundary-whole-qualified-v1/manifest.safe.json').read_bytes())
    literal = json.loads((W / 'pg3952-literal-candidate-v1/manifest.safe.json').read_bytes()); applied = json.loads((W / 'pg3960-literal-candidate-material-v1/apply.safe.json').read_bytes())
    after = json.loads((W / 'pg3964-prior-invariant-after-v1/manifest.safe.json').read_bytes())
    require(full['actualExit'] == literal['actualExit'] == applied['actualExit'] == after['actualExit'] == 0 and full['result']['tests'] == 3716 and applied['changedMainFiles'] == 71 and after['mainSource'] == SOURCE and after['result']['tests'] == 7 and after['result']['targetClassFour100'] is True, 'all independent grouped preconditions')
    changes = set(subprocess.check_output(['git', 'diff', '--name-only', full['result']['sourceSnapshot'], head, '--', *previous.previous.base.SCOPE], cwd=ROOT, text=True).splitlines())
    require(changes == set(literal['result']['changes']) | {MAIN, TEST}, 'all and only proven71 literal Main plus one constructor and its single Test')
    expected = {**literal['result']['allCandidateSourceSha256'], MAIN: __import__('hashlib').sha256((ROOT / MAIN).read_bytes()).hexdigest()}
    require(expected == {str(p.relative_to(ROOT)): __import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('src/*/src/main/java/**/*.java')}, 'every original/proven849 source byte')
    require(not subprocess.check_output(['git', 'diff', after['testSource'], head, '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=ROOT), 'all actual after-tested source/Tests unchanged')
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'clean frozen campaign')


def server_source(head, digest):
    h, d = 'a2' * 20, 'b3' * 32
    return rebase(previous.server_source(h, d), 'PG3734', 'PG3966', 3714, 3717, {h: head, d: digest, previous.SOURCE: SOURCE})


def operator_source():
    raw = inspect.getsource(previous.main).replace('PG3734', 'PG3966').replace('pg3734', 'pg3966').replace('3714', '3717')
    for old, new in [('3712 retained plus exact two independent Root inode value/ACL boundary cases;545suite1643Main; batched semantic-proof source hygiene', BASIS), ('BUG1312 Test boundary plus BUG1313/1317/1320 batched cross-module Main hygiene; required one fresh whole, old4856 native not candidate credit', TRIGGER)]:
        require(raw.count(old) == 1, 'exact honest campaign metadata'); raw = raw.replace(old, new)
    return raw


def main():
    values = {**previous.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server_source': server_source}
    exec(compile(operator_source(), '<one combined3717 new-Main campaign>', 'exec'), values)
    return values['main']()


if __name__ == '__main__':
    raise SystemExit(main())
