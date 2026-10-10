"""Literal journal/DONE fixtures, independent negative identity/budget oracle."""
import copy
import unittest
from pg1116_current_receipt import qualify


class ReceiptTest(unittest.TestCase):
    def fixture(self):
        binding = dict(boot='cbca87383b244090b77cbf029677cdd6',
                       invocation='21f20c0cdbe34ce99431a55b10f92285',
                       job='36002', start=34658346852,
                       run='11111111-1111-4111-8111-111111111111',
                       activation='22222222-2222-4222-8222-222222222222',
                       cutoff='2026-10-10T12:40:27.000000Z')
        row = dict(_BOOT_ID='cbca87383b244090b77cbf029677cdd6', _PID='1',
                   _UID='0', _COMM='systemd', UNIT='schubert-nk-morning-controller.service',
                   INVOCATION_ID='21f20c0cdbe34ce99431a55b10f92285',
                   __MONOTONIC_TIMESTAMP='34673346852',
                   __REALTIME_TIMESTAMP='1791636040000000', __CURSOR='literal-one')
        first = dict(row, MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',
                     JOB_ID='36002', JOB_TYPE='start', JOB_RESULT='done')
        second = dict(row, MESSAGE_ID='7ad2d189f7e94e70a38c781354912448',
                      __CURSOR='literal-two')
        done = (b'NKDONE1\n11111111-1111-4111-8111-111111111111\n'
                b'2026-10-10T12:40:27.000000Z\n22222222-2222-4222-8222-222222222222\n'
                b'2026-10-10T12:40:39.000000Z\n0\n')
        return binding, [first, second], done

    def test_literal_receipt(self):
        binding, rows, done = self.fixture()
        self.assertEqual(qualify(binding, rows, done), {
            'genuinePid1StartDone': True, 'genuineRootDone': True,
            'endMonotonicUs': 34673346852, 'elapsedSeconds': 15.0,
            'sameRunActivationCutoff': True})

    def test_binding_null_unknown_old_and_interval(self):
        binding, rows, done = self.fixture()
        cases = [None, {}, dict(binding, extra=0)]
        for key in binding:
            cases.append(dict(binding, **{key: None}))
        cases += [dict(binding, start=True), dict(binding, job='old'),
                  dict(binding, cutoff='2026-10-09T23:31:22.087768Z'),
                  dict(binding, cutoff='2026-10-10T13:10:26.000000Z'),
                  dict(binding, cutoff='2026-10-10T12:40:27+00:00'),
                  dict(binding, run='11111111-1111-1111-8111-111111111111')]
        for value in cases:
            with self.subTest(binding=value), self.assertRaises(ValueError):
                qualify(value, rows, done)

    def test_each_journal_identity_and_job_rejected(self):
        binding, rows, done = self.fixture()
        keys = ['_BOOT_ID', '_PID', '_UID', '_COMM', 'UNIT', 'INVOCATION_ID',
                '__MONOTONIC_TIMESTAMP', 'JOB_RESULT',
                'MESSAGE_ID', 'JOB_ID', 'JOB_TYPE', '__REALTIME_TIMESTAMP']
        for key in keys:
            value = copy.deepcopy(rows); value[0][key] = 'wrong'
            with self.subTest(key=key), self.assertRaises(ValueError):
                qualify(binding, value, done)
        for value in [None, [], [rows[0]], rows + [rows[0]]]:
            with self.assertRaises(ValueError): qualify(binding, value, done)
        for cursor in ['', 'literal-two', None]:
            value = copy.deepcopy(rows); value[0]['__CURSOR'] = cursor
            with self.assertRaises(ValueError): qualify(binding, value, done)

    def test_done_malformed_and_budget_boundaries(self):
        binding, rows, done = self.fixture()
        for value in [None, b'', done[:-1], done.replace(b'NKDONE1', b'NKDONE0'),
                      done.replace(b'11111111', b'33333333'),
                      done.replace(b'22222222', b'44444444'),
                      done.replace(b'39.000000Z', b'41.000000Z'),
                      done[:-2] + b'1\n']:
            with self.assertRaises((ValueError, UnicodeError)):
                qualify(binding, rows, value)
        for stamp in ['34658346851', '36458346853']:
            value = copy.deepcopy(rows); value[0]['__MONOTONIC_TIMESTAMP'] = stamp
            with self.assertRaises(ValueError): qualify(binding, value, done)


if __name__ == '__main__': unittest.main()
