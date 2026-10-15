"""Complete only the known pre-start partial prepare, never replay its writes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import pg3218_legacy_negative_retained as cohort
import pg3216_legacy_negative_observer as observer


def configure():
    cohort.OUT = cohort.BASE / 'observer-cohort-v3'
    cohort.DROP = Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/zz-pg3222-negative-fixture.conf')
    cohort.CASE_NAME = 'case-cohort-v3'; cohort.NATIVE_NAME = 'cohort-native-v3.exec'; cohort.SESSION_ID = 'PG3222-LFACT-v3'


def complete_prepare():
    observer.guard(); cohort.runtime_fixed(); require = observer.require
    require(cohort.OUT.is_dir() and not cohort.OUT.is_symlink() and not list(cohort.OUT.iterdir()))
    require(not (cohort.BASE / cohort.CASE_NAME).exists() and not (cohort.BASE / cohort.NATIVE_NAME).exists())
    before = json.loads((cohort.BASE / 'observer-cohort-v2/before.private.json').read_text())
    require(observer.tree() == before['tree'] and observer.database() == before['database'] and observer.stable_bad() == before['bad'])
    original = json.loads((cohort.BASE / 'setup.safe.json').read_text())
    require(observer.sha(observer.DROP) == original['unitDropinSha256'])
    text = observer.DROP.read_text().replace('case-cohort-v1', cohort.CASE_NAME).replace('cohort-native.exec', cohort.NATIVE_NAME).replace('sessionid=PG3216-LFACT-v1', 'sessionid=' + cohort.SESSION_ID) + 'RemainAfterExit=yes\n'
    s = cohort.DROP.lstat()
    require(stat.S_ISREG(s.st_mode) and s.st_uid == s.st_gid == 0 and stat.S_IMODE(s.st_mode) == 0o644 and s.st_nlink == 1 and cohort.DROP.read_text() == text)
    u = observer.unit(); require(u['ActiveState'] == 'inactive' and u['MainPID'] == u['ControlPID'] == '0' and u['Job'] == '')
    observer.no_exit_hooks()  # Typed load/read only, no reload/start/stop.
    proof = {'actualExit': 0, 'boot': observer.BOOT, 'source': observer.SOURCE, 'oldFailedWhole': 1, 'oldFailedNativeImported': False,
             'unitDropinSha256': hashlib.sha256(text.encode()).hexdigest(), 'originalRuntime': original, 'newCasesRun': 0,
             'completedKnownPartialPrepareWithoutReissuingWrites': True, 'formalAccepted': False}
    with (cohort.OUT / 'setup.safe.json').open('x') as file:
        json.dump(proof, file, sort_keys=True); file.flush(); os.fsync(file.fileno())


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=['prepare', 'execute']); phase = parser.parse_args().phase
    configure()
    (complete_prepare if phase == 'prepare' else cohort.execute)()


if __name__ == '__main__':
    main()
