import copy
import datetime
import unittest
from pg1185_current_resume_receipt import qualify, CURRENT


class ResumeReceiptTest(unittest.TestCase):
    def fixture(self):
        binding = dict(CURRENT, run='343a5a1b-d064-47d5-88c2-31c36d7ba7a4', cutoff='2026-10-10T12:40:27.396847Z', activation='ada3f7ff-8287-48d7-9ba9-5cce71f61bd3')
        row = {'_BOOT_ID': CURRENT['boot'], '_PID': '1', '_UID': '0', '_COMM': 'systemd', 'UNIT': 'schubert-nk-morning-controller.service', 'INVOCATION_ID': CURRENT['invocation'], '__MONOTONIC_TIMESTAMP': '51187132518', '__REALTIME_TIMESTAMP': str(int(datetime.datetime(2026,10,10,17,15,51,tzinfo=datetime.timezone.utc).timestamp()*1_000_000)), '__CURSOR': 'literal-fresh-one'}
        first = dict(row, MESSAGE_ID='39f53479d3a045ac8e11786248231fbf', JOB_ID='81093', JOB_TYPE='start', JOB_RESULT='done')
        second = dict(row, MESSAGE_ID='7ad2d189f7e94e70a38c781354912448', __CURSOR='literal-fresh-two')
        done = b'NKDONE1\n343a5a1b-d064-47d5-88c2-31c36d7ba7a4\n2026-10-10T12:40:27.396847Z\nada3f7ff-8287-48d7-9ba9-5cce71f61bd3\n2026-10-10T17:15:50.000000Z\n0\n'
        return binding, [first, second], done

    def test_current_root_original_and_literal_success(self):
        binding, rows, done = self.fixture()
        self.assertEqual(qualify(binding, rows, done), {'genuinePid1StartDone': True, 'genuineRootDone': True, 'endMonotonicUs': 51187132518, 'elapsedSeconds': 15.0, 'sameRunActivationCutoff': True})

    def test_old_generation_unknown_null_and_every_journal_identity(self):
        binding, rows, done = self.fixture()
        for key in binding:
            with self.assertRaises((ValueError, TypeError)):qualify(dict(binding, **{key: None}), rows, done)
        for key, value in [('invocation', '21f20c0cdbe34ce99431a55b10f92285'), ('job', '36002'), ('start', 34658346852)]:
            with self.assertRaises(ValueError):qualify(dict(binding, **{key: value}), rows, done)
        for key in ['_BOOT_ID','_PID','_UID','_COMM','UNIT','INVOCATION_ID','__MONOTONIC_TIMESTAMP','JOB_RESULT','MESSAGE_ID','JOB_ID','JOB_TYPE','__REALTIME_TIMESTAMP']:
            bad = copy.deepcopy(rows);bad[0][key] = 'foreign'
            with self.subTest(key=key), self.assertRaises(ValueError):qualify(binding, bad, done)
        for value in ['', None, 'literal-fresh-two']:
            bad = copy.deepcopy(rows);bad[0]['__CURSOR'] = value
            with self.assertRaises(ValueError):qualify(binding, bad, done)

    def test_budget_done_malformed_duplicate_and_terminal_not_ready(self):
        binding, rows, done = self.fixture()
        for stamp in ['51172132517', '52972132519']:
            bad = copy.deepcopy(rows);bad[0]['__MONOTONIC_TIMESTAMP'] = stamp
            with self.assertRaises(ValueError):qualify(binding, bad, done)
        for bad in [None, [], [rows[0]], rows + [rows[0]]]:
            with self.assertRaises(ValueError):qualify(binding, bad, done)
        for bad in [None, b'', done[:-1], done.replace(b'NKDONE1', b'NKDONE0'), done.replace(b'ada3f7ff', b'aaaaaaaa'), done.replace(b'343a5a1b', b'bbbbbbbb'), done[:-2]+b'1\n']:
            with self.assertRaises((ValueError, UnicodeError)):qualify(binding, rows, bad)


if __name__ == '__main__':unittest.main()
