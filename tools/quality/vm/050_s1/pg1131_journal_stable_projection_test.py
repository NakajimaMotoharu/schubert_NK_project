import unittest
from pg1131_journal_stable_projection import project


class JournalTest(unittest.TestCase):
    def test_order_only_changes_and_empty_are_independently_equivalent(self):
        a = b'{"__CURSOR":"one","MESSAGE":"literal","NUMBER":[1,2],"MULTI":["a","b"]}\n'
        b = b'{"MULTI":["a","b"],"NUMBER":[1,2],"MESSAGE":"literal","__CURSOR":"one"}\n'
        self.assertEqual(project(a), project(b))
        self.assertEqual(project(b''), b'[]\n')
        self.assertIn(b'"NUMBER":[1,2]', project(a))

    def test_every_field_and_event_order_are_significant(self):
        a = b'{"__CURSOR":"one","MESSAGE":"a"}\n{"__CURSOR":"two","MESSAGE":"b"}\n'
        b = b'{"__CURSOR":"two","MESSAGE":"b"}\n{"__CURSOR":"one","MESSAGE":"a"}\n'
        self.assertNotEqual(project(a), project(b))
        self.assertNotEqual(project(a), project(a.replace(b'"a"', b'"changed"')))
        self.assertNotEqual(project(a), project(a.replace(b'"MESSAGE":"a"', b'"OTHER":"a"')))

    def test_duplicate_unknown_schema_invalid_cursor_and_null_refused(self):
        for raw in [None, 'text', b'null', b'[]', b'{}', b'{"__CURSOR":null}',
                    b'{"__CURSOR":""}', b'{"__CURSOR":"one","__CURSOR":"one"}',
                    b'{"__CURSOR":"one","UNKNOWN":null}', b'{"__CURSOR":"one","FLAG":true}',
                    b'{"__CURSOR":"one"}\n{"__CURSOR":"one"}\n']:
            with self.subTest(raw=raw), self.assertRaises((ValueError, TypeError)): project(raw)


if __name__ == '__main__': unittest.main()
