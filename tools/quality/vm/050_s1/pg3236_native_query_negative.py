"""Fresh v5: actual default FFI public read, no private socket or unsafe exec."""
import argparse
import json
import os
from pathlib import Path
import pg3218_legacy_negative_retained as cohort


def reset_known_failed():
    o = cohort.observer; o.guard(); cohort.runtime_fixed(); require = o.require
    old = cohort.BASE / 'observer-cohort-v4'
    require(json.loads((old / 'failed.safe.json').read_text()) == {'actualExit': 1, 'casesPassed': 0, 'nativeAccepted': False, 'type': 'ValueError'})
    setup = json.loads((old / 'setup.safe.json').read_text())
    drop = Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/zz-pg3230-negative-fixture.conf')
    require(o.sha(drop) == setup['unitDropinSha256'] and setup['boot'] == o.BOOT)
    before = json.loads((old / 'before.private.json').read_text())
    require(o.tree() == before['tree'] and o.database() == before['database'] and o.stable_bad() == before['bad'])
    u = o.unit()
    require(u['ActiveState'] == u['SubState'] == 'failed' and u['MainPID'] == u['ControlPID'] == '0' and u['Job'] == ''
            and u['ExecMainCode'] == '1' and u['ExecMainStatus'] == '1' and u['InvocationID'] == 'e4b30a31e37247c7b21ddbb5e56d42bc')
    group = Path('/sys/fs/cgroup/system.slice') / o.UNIT
    require(not group.exists() or not (group / 'cgroup.procs').read_text().strip())
    o.RESULTS = old
    o.save('reset-failed-reservation.safe.json', {'issuedOnce': True, 'oldFailed': u, 'oldNativeAccepted': False})
    require(o.unit() == u); o.command(['systemctl', 'reset-failed', o.UNIT])
    after = o.unit(); require(after['ActiveState'] == 'inactive' and after['MainPID'] == after['ControlPID'] == '0' and after['Job'] == '')
    o.save('reset-failed.safe.json', {'actualExit': 0, 'oldNativeAccepted': False, 'businessStarts': 0})


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=['prepare', 'execute', 'retire-failed']); phase = parser.parse_args().phase
    if phase == 'retire-failed': reset_known_failed(); return
    cohort.OUT = cohort.BASE / 'observer-cohort-v5'
    cohort.DROP = Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/zz-pg3236-negative-fixture.conf')
    cohort.CASE_NAME = 'case-cohort-v5'; cohort.NATIVE_NAME = 'cohort-native-v5.exec'; cohort.SESSION_ID = 'PG3236-LFACT-v5'
    {'prepare': cohort.prepare, 'execute': cohort.execute}[phase]()


if __name__ == '__main__':
    main()
