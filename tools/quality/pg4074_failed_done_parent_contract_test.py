import copy
import unittest
import pg4074_failed_done_parent_contract as contract


def fixture():
    state = {'Id': 'schubert-nk-morning-controller.service', 'LoadState': 'loaded',
             'ActiveState': 'failed', 'SubState': 'failed', 'InvocationID': '820851b8291a4c958bb34f6c48430ca3',
             'MainPID': '0', 'ControlPID': '0', 'Job': '', 'Result': 'timeout', 'ExecMainCode': '1',
             'ExecMainStatus': '143', 'ExecMainStartTimestampMonotonic': '128735401165',
             'ExecMainExitTimestampMonotonic': '130535470134'}
    base = {'UNIT': 'schubert-nk-morning-controller.service', 'INVOCATION_ID': '820851b8291a4c958bb34f6c48430ca3',
            '_PID': '1', '_UID': '0', '_BOOT_ID': '79a3260ae16d42bf942ab914ed144c28'}
    rows = [{**base, 'MESSAGE_ID': '7d4958e842da4a758f6c1cdc7b36dcc5', 'JOB_ID': '155272',
             'JOB_TYPE': 'start', '__MONOTONIC_TIMESTAMP': '128735402355'},
            {**base, 'MESSAGE_ID': 'be02cf6855d2428ba40df7e9d022f03d', 'JOB_ID': '155272',
             'JOB_TYPE': 'start', 'JOB_RESULT': 'failed', '__MONOTONIC_TIMESTAMP': '130535471617'}]
    done = (b'NKDONE1\ndc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f\n2026-10-16T05:44:47.267413Z\n'
            b'd9d58371-bf80-49f6-bad9-3d1e0916fb04\n2026-10-16T06:14:11.517417Z\n10\n')
    return state, rows, done


def subject(state, rows, done, source=None, bom=None, boot=None):
    return contract.classify(contract.SOURCE if source is None else source,
                            contract.BOM if bom is None else bom, contract.BOOT if boot is None else boot,
                            state, rows, done)


class FailedDoneTest(unittest.TestCase):
    def test_actual_shape_never_confers_normal_or_stop(self):
        v = subject(*fixture())
        self.assertTrue(v['failedParent143Confirmed'] and v['actualPid1StartFailed'])
        self.assertTrue(v['completedOriginalWarningDataConfirmed'])
        for k in ['parentNormal', 'genuineRootDone', 'genuinePid1StartDone', 'normalUnit0or10',
                  'recoveryAuthorityIssued', 'stopAuthority', 'formalAccepted']:
            self.assertIs(v[k], False)
        self.assertEqual(1800.068969, v['elapsedSeconds'])

    def test_identity_and_state_cannot_be_rebound(self):
        for key, replacement in [('ExecMainStatus', '0'), ('ExecMainStatus', '10'),
                ('Result', 'success'), ('InvocationID', '0' * 32), ('MainPID', '696557'),
                ('ActiveState', 'inactive'), ('Job', '155272'), ('ExecMainCode', '2'),
                ('ControlPID', '123'), ('ExecMainStartTimestampMonotonic', '128735401166')]:
            s, r, d = fixture(); s[key] = replacement
            with self.subTest(key=key), self.assertRaises(ValueError): subject(s, r, d)
        for key in ['source', 'bom', 'boot']:
            with self.subTest(key=key), self.assertRaises(ValueError): subject(*fixture(), **{key: 'foreign'})

    def test_real_failed_job_not_done_missing_duplicate_or_foreign(self):
        for mode in ['done', 'duplicate', 'missing', 'wrongjob', 'wrongpid', 'wrongboot', 'late', 'early', 'nonnumeric', 'null']:
            s, r, d = fixture()
            if mode == 'done': r[1]['JOB_RESULT'] = 'done'
            elif mode == 'duplicate': r.append(copy.deepcopy(r[0]))
            elif mode == 'missing': r.pop()
            elif mode == 'wrongjob': r[1]['JOB_ID'] = '155273'
            elif mode == 'wrongpid': r[0]['_PID'] = '2'
            elif mode == 'wrongboot': r[0]['_BOOT_ID'] = '0' * 32
            elif mode == 'late': r[1]['__MONOTONIC_TIMESTAMP'] = '130545470135'
            elif mode == 'early': r[1]['__MONOTONIC_TIMESTAMP'] = '128735402356'
            elif mode == 'nonnumeric': r[0]['__MONOTONIC_TIMESTAMP'] = 'nan'
            else: r[0]['_UID'] = None
            with self.subTest(mode=mode), self.assertRaises(ValueError): subject(s, r, d)

    def test_null_malformed_and_other_completion_cannot_be_accepted(self):
        for replacement in [None, b'', b'unknown', fixture()[2].replace(b'\n10\n', b'\n0\n'),
                            fixture()[2] + b'\n', fixture()[2].decode()]:
            s, r, _ = fixture()
            with self.subTest(done_type=type(replacement)), self.assertRaises(ValueError): subject(s, r, replacement)
        for position in [0, 1]:
            values = list(fixture()); values[position] = None
            with self.assertRaises(ValueError): subject(*values)


if __name__ == '__main__': unittest.main()
