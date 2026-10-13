"""Necessary fresh all-source regression for strict EOF/current-run Main candidate."""
import inspect
import json
import subprocess
import pg2494_current_boundary_full_six as previous

SOURCE = 'a79b45b5858a186fa82bec1ff36882271ab996a4'
SCOPE = ['src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']


def production():
    return SOURCE


def validate(snapshot):
    root = previous.previous.transport.prior.ROOT
    receipt = json.loads((root / 'evidence/01_PT/018_NK-OPS-001/evidence/strict-current-reference/manifest-v2.json').read_bytes())
    if (type(receipt.get('actualExit')) is not int or receipt['actualExit'] != 0
            or receipt.get('changedMethodScopeComplete') is not True
            or receipt.get('wholeClassFour100Accepted') is not False):
        raise ValueError('actual independent changed-method result required, not whole-class acceptance')
    for ref in [SOURCE, receipt['sourceSnapshot']]:
        if subprocess.check_output(['git', 'diff', ref, snapshot, '--', *SCOPE], cwd=root):
            raise ValueError('frozen selected and candidate source must equal full snapshot')


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG2494', 'PG2510').replace('3649', '3650').replace(previous.SOURCE, SOURCE)
    compile(raw, '<fresh Main candidate full3650>', 'exec')
    return raw


def main():
    transport = previous.previous.transport
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=transport.prior.ROOT, text=True).strip()
    validate(head)
    raw = inspect.getsource(transport.main)
    for a, b in [('PG1528', 'PG2510'), ('pg1528', 'pg2510'), ('3582', '3650'), ('524', '540'), ('1637', '1643')]:
        raw = raw.replace(a, b)
    raw = raw.replace('3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained',
                      '3649 retained plus one independent currentRunReference test; two Main candidate changes; 540 suites/1643 Main')
    raw = raw.replace('SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved',
                      'PG-D417 internal strict EOF and data-only same-run reference; new Main requires fresh full and new runtime/native qualification')
    ns = {**transport.__dict__, 'PRODUCTION': SOURCE, 'server_source': server_source}
    exec(compile(raw, '<PG2510 fresh full transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
