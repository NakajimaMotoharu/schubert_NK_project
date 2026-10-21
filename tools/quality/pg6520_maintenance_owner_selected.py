"""Self TempDir opaque fixed reader; no real owner/credential or authority access."""
import json
import subprocess
from pg5940_private_lock_compile import ROOT, W, BASE, sha
import finite_selected_profile as profile

OLD = 'c2486f0107633c2670da5ed68d244cc62349657a'
TEST = 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/MaintenanceOwnerCredentialReaderTest.java'
SLOT = 'pg6520-maintenance-owner-reader-v1'
Q = BASE/'PG6518-caddy-identity-qualification-v1/manifest.json'
QSHA = 'e4e52e91f76bbcd9110478341c46acc97a13c5bc892d56bc6175239ed42e2344'


def inventory():
    return profile.inventory({'bootstrap': {'api.file.MaintenanceOwnerCredentialReaderTest'}}, (15, 8))


def guard_source(source):
    if sha(Q) != QSHA:
        raise ValueError('immutable original15 qualification first')
    q = json.loads(Q.read_bytes())
    if not (q['source'] == OLD and q['actualExit'] == 0 and not q['changedPhysical']
            and (q['tests'], q['suites'], q['sourceFiles'], q['physicalMain']) == (15, 8, 851, 1667)):
        raise ValueError('same-source original15 all-Main invariant')
    if subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'],
                               cwd=ROOT, text=True).splitlines() != [TEST]:
        raise ValueError('only new independent reader Test; all Main and old oracle unchanged')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn',
                               'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('gates and Current unchanged')


def main():
    cases, counts = inventory()
    return profile.execute(SLOT, guard_source, cases, counts, (15, 8),
                           {'bootstrap': ['api/file/InspectorCredentialLoader']})


if __name__ == '__main__':
    raise SystemExit(main())
