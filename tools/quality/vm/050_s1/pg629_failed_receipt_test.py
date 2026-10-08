"""Independent literals and one-field rejection matrix, no Production import."""
import copy
import unittest
from pg629_failed_receipt import failed30


def literal():
    messages = [
        ('7d4958e842da4a758f6c1cdc7b36dcc5', '97060187042', {'JOB_ID': '98394', 'JOB_TYPE': 'start'}),
        ('98e322203f7a4ed290d09fe03c09fe15', '97094172037', {'EXIT_CODE': 'exited', 'EXIT_STATUS': '30'}),
        ('d9b373ed55a64feb8242e02dbe79a49c', '97094172347', {}),
        ('be02cf6855d2428ba40df7e9d022f03d', '97094172397', {'JOB_ID': '98394', 'JOB_TYPE': 'start', 'JOB_RESULT': 'failed'}),
        ('ae8f7b866b0347b9af31fe1c80b127c0', '97094172443', {}),
    ]
    return [dict(_BOOT_ID='cc9ed8747f4f450ea1888de1e42c8441', _PID='1',
                 _UID='0', _COMM='systemd', UNIT='schubert-nk-morning-controller.service',
                 INVOCATION_ID='3a2de24f931544c0a2fd83556a659cd0',
                 MESSAGE_ID=msg, __MONOTONIC_TIMESTAMP=stamp, __CURSOR='fixture-' + str(i), **fields)
            for i, (msg, stamp, fields) in enumerate(messages)]


class Receipt(unittest.TestCase):
    def test_exact_failure_not_normal(self):
        rows = literal(); before = copy.deepcopy(rows)
        self.assertEqual(failed30(rows), {'startMonotonicUs': 97060184910,
            'endMonotonicUs': 97094171993, 'status': 30, 'elapsedSeconds': 33.987083,
            'oldScopesNormalized': False})
        self.assertEqual(rows, before)

    def test_mutations(self):
        for index, row in enumerate(literal()):
            for key in row:
                for value in (None, '', 1, False, 'foreign'):
                    if key == '__CURSOR' and value == 'foreign':
                        continue  # Cursor contents are private; exact actual rows bind at baseline equality.
                    changed = literal(); changed[index][key] = value
                    with self.subTest(index=index, key=key, value=value), self.assertRaises(ValueError):
                        failed30(changed)
            changed = literal(); changed[index]['__CURSOR'] = 'fixture-0'
            if index:
                with self.assertRaises(ValueError): failed30(changed)
        for rows in (None, {}, [], literal()[:-1], literal() + [literal()[0]], list(reversed(literal()))):
            with self.assertRaises(ValueError): failed30(rows)
        for status in ('0', '143', '10'):
            changed = literal(); changed[1]['EXIT_STATUS'] = status
            with self.assertRaises(ValueError): failed30(changed)


if __name__ == '__main__': unittest.main()
