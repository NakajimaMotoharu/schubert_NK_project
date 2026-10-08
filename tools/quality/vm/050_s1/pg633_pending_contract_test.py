"""Independent nineteen-field finite delta, all protected fields and typed negatives."""
import copy
import hashlib
import stat
import unittest
from pg633_pending_contract import changed_only, phase_action, same_value


FIELDS = 'backup bootstrapOldProofs bootstrapTools configuration credentials dependencies native oldProofs originals parentPid1 pid1Stop rows runtime startup units current approval unitFiles caddyPre'.split()
NEW = b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG631\nmanifest_sha256=57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe\n'


def fixture():
    before = {key: {'literal': ['unchanged', 1, True]} for key in FIELDS}
    before['runtime'] = None; before['current'] = '/opt/schubert-nk/releases/0.1.0-PG621'
    before['startup'] = {'epoch.current': {'sha256': 'independent-invalid'}, 'keep': 'literal'}
    before['approval'] = {'metadata': [31, 42, 0, 0, stat.S_IFREG | 0o400, 1, 139, 100, 100], 'sha256': 'old-literal'}
    after = copy.deepcopy(before); after['current'] = '/opt/schubert-nk/releases/0.1.0-PG631'
    after['approval'] = {'metadata': [31, 43, 0, 0, stat.S_IFREG | 0o400, 1, len(NEW), 101, 101], 'sha256': hashlib.sha256(NEW).hexdigest()}
    return before, after


class Contract(unittest.TestCase):
    def test_only_approval_current_no_epoch_delta(self):
        before, after = fixture(); old = copy.deepcopy((before, after))
        self.assertTrue(changed_only(before, after)); self.assertEqual((before, after), old)
        self.assertTrue(same_value({'v': [None, False, 1, 'x', 1.0]}, {'v': [None, False, 1, 'x', 1.0]}))
        for a, b in [(True, 1), (1, 1.0), (float('nan'), float('nan')), ({1: 'a'}, {1: 'a'}), ([1], [1, 2])]:
            self.assertFalse(same_value(a, b))

    def test_every_protected_field_and_namespace(self):
        for key in FIELDS:
            if key in ('current', 'approval'): continue
            before, after = fixture(); after[key] = {'foreign': True}
            with self.subTest(key=key), self.assertRaises(ValueError): changed_only(before, after)
            before, after = fixture(); after.pop(key)
            with self.assertRaises(ValueError): changed_only(before, after)
        for which in (0, 1):
            before, after = fixture(); (before, after)[which]['extra'] = 0
            with self.assertRaises(ValueError): changed_only(before, after)
        for value in (None, {}, [], False):
            before, after = fixture()
            with self.assertRaises(ValueError): changed_only(value, after)
            with self.assertRaises(ValueError): changed_only(before, value)

    def test_approval_all_metadata_and_hash_types(self):
        for index, value in [(0, 32), (1, 42), (1, 0), (2, 1), (3, 1),
                             (4, stat.S_IFREG | 0o600), (5, 2), (6, len(NEW) + 1)]:
            before, after = fixture(); after['approval']['metadata'][index] = value
            with self.subTest(index=index), self.assertRaises(ValueError): changed_only(before, after)
        for index in range(9):
            before, after = fixture(); after['approval']['metadata'][index] = True
            with self.assertRaises(ValueError): changed_only(before, after)
        for value in (None, '', '0' * 64, hashlib.sha256(NEW + b'x').hexdigest()):
            before, after = fixture(); after['approval']['sha256'] = value
            with self.assertRaises(ValueError): changed_only(before, after)
        before, after = fixture(); after['current'] = before['current']
        with self.assertRaises(ValueError): changed_only(before, after)

    def test_phase(self):
        self.assertEqual(phase_action('READY', 'before'), 'READY')
        self.assertEqual(phase_action('READY', 'after'), 'CHECKED')
        self.assertEqual(phase_action('CHECKED', 'release'), 'CLOSED')
        for a, b in [('READY', 'release'), ('CHECKED', 'before'), ('CLOSED', 'release'),
                     (None, 'before'), ('READY', None), ('foreign', 'after')]:
            with self.assertRaises(ValueError): phase_action(a, b)


if __name__ == '__main__': unittest.main()
