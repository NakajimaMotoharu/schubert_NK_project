"""Third fresh cohort; typed D-Bus preflight and finite old-failure retirement."""
import argparse
import os
from pathlib import Path
import pg3218_legacy_negative_retained as cohort


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=['prepare', 'execute', 'retire-failed']); phase = parser.parse_args().phase
    if phase == 'retire-failed': cohort.retire_failed(); return
    cohort.OUT = cohort.BASE / 'observer-cohort-v3'
    cohort.DROP = Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/zz-pg3222-negative-fixture.conf')
    cohort.CASE_NAME = 'case-cohort-v3'; cohort.NATIVE_NAME = 'cohort-native-v3.exec'; cohort.SESSION_ID = 'PG3222-LFACT-v3'
    {'prepare': cohort.prepare, 'execute': cohort.execute}[phase]()


if __name__ == '__main__':
    main()
