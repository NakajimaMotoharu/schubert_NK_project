"""Fourth fresh cohort: public bus bounded, private path kernel syscall witness."""
import argparse
import os
from pathlib import Path
import subprocess
import pg3218_legacy_negative_retained as cohort


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=['prepare', 'execute']); phase = parser.parse_args().phase
    cohort.observer.guard()
    cohort.OUT = cohort.BASE / 'observer-cohort-v4'
    cohort.DROP = Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/zz-pg3230-negative-fixture.conf')
    cohort.CASE_NAME = 'case-cohort-v4'; cohort.NATIVE_NAME = 'cohort-native-v4.exec'; cohort.SESSION_ID = 'PG3230-LFACT-v4'
    if phase == 'prepare':
        # Real local OS capability preflight, not another business/Unit run.
        child = subprocess.Popen(['/usr/bin/sleep', '1'])
        trace = subprocess.run(['/usr/bin/strace', '-f', '-qq', '-e', 'trace=execve,connect', '-p', str(child.pid)], capture_output=True, timeout=5)
        cohort.observer.require(child.wait(timeout=5) == 0 and trace.returncode == 0)
        cohort.prepare()
    else: cohort.execute()


if __name__ == '__main__':
    main()
