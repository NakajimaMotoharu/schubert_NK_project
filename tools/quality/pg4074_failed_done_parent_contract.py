"""BUG1332 data-only failed-DONE certificate. Never a normal receipt or stop authority."""
import hashlib

SOURCE = '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e'
BOM = '0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab'
BOOT = '79a3260a-e16d-42bf-942a-b914ed144c28'
INVOCATION = '820851b8291a4c958bb34f6c48430ca3'
JOB = '155272'
START = 128735401165
EXIT = 130535470134
UNIT = 'schubert-nk-morning-controller.service'
DONE_SHA = 'ca7829dbf4f1f215bc9bc6c60dd02c94137e2157a665ee57905b3c2aa5f0d090'
STARTING = '7d4958e842da4a758f6c1cdc7b36dcc5'
FAILED = 'be02cf6855d2428ba40df7e9d022f03d'


def require(value):
    if value is not True: raise ValueError('fixed failed-DONE parent evidence refused')


def classify(source, bom, boot, state, rows, done):
    require(source == SOURCE and bom == BOM and boot == BOOT)
    require(type(state) is dict and all(type(k) is str and type(v) is str for k, v in state.items()))
    expected = {'Id': UNIT, 'LoadState': 'loaded', 'ActiveState': 'failed', 'SubState': 'failed',
                'InvocationID': INVOCATION, 'MainPID': '0', 'ControlPID': '0', 'Job': '',
                'Result': 'timeout', 'ExecMainCode': '1', 'ExecMainStatus': '143',
                'ExecMainStartTimestampMonotonic': str(START), 'ExecMainExitTimestampMonotonic': str(EXIT)}
    require(all(state.get(k) == v for k, v in expected.items()))
    require(type(done) is bytes and hashlib.sha256(done).hexdigest() == DONE_SHA)
    # Fixed independently observed bytes, not Production MaintenanceRecords.decode as oracle.
    require(done.split(b'\n') == [b'NKDONE1', b'dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f',
            b'2026-10-16T05:44:47.267413Z', b'd9d58371-bf80-49f6-bad9-3d1e0916fb04',
            b'2026-10-16T06:14:11.517417Z', b'10', b''])
    require(type(rows) is list and 2 <= len(rows) <= 32)
    starts = []; failures = []; seen = set()
    for r in rows:
        require(type(r) is dict and all(type(k) is str and type(v) is str for k, v in r.items()))
        require(all(r.get(k) == v for k, v in {'UNIT': UNIT, 'INVOCATION_ID': INVOCATION,
                    '_PID': '1', '_UID': '0', '_BOOT_ID': BOOT.replace('-', '')}.items()))
        stamp = r.get('__MONOTONIC_TIMESTAMP', '')
        require(stamp.isascii() and stamp.isdecimal() and str(int(stamp)) == stamp)
        at = int(stamp); require(START <= at <= EXIT + 10_000_000 and at not in seen); seen.add(at)
        require('JOB_RESULT' not in r or r['JOB_RESULT'] == 'failed')
        if r.get('MESSAGE_ID') == STARTING:
            require(r.get('JOB_ID') == JOB and r.get('JOB_TYPE') == 'start' and 'JOB_RESULT' not in r)
            require(START <= at <= START + 1_000_000); starts.append(at)
        elif r.get('MESSAGE_ID') == FAILED:
            require(r.get('JOB_ID') == JOB and r.get('JOB_TYPE') == 'start' and r.get('JOB_RESULT') == 'failed')
            require(EXIT <= at <= EXIT + 10_000_000); failures.append(at)
        else:
            require('JOB_ID' not in r and 'JOB_TYPE' not in r and 'JOB_RESULT' not in r)
    require(len(starts) == len(failures) == 1 and starts[0] < failures[0])
    return {'failedParent143Confirmed': True, 'actualPid1StartFailed': True,
            'completedOriginalWarningDataConfirmed': True, 'doneSha256': DONE_SHA,
            'parentNormal': False, 'genuineRootDone': False, 'genuinePid1StartDone': False,
            'normalUnit0or10': False, 'recoveryAuthorityIssued': False, 'stopAuthority': False,
            'formalAccepted': False, 'elapsedSeconds': (EXIT - START) / 1_000_000}
