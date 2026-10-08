"""Independent literal WBS JSON duplicate rejection; no acceptance granted."""
import json
import unittest
from wbs_progress_audit import unique_object


class Duplicate(unittest.TestCase):
    def test_top_and_nested_duplicate_rejected(self):
        for text in ('{"current":1,"current":2}', '{"nested":{"source":1,"source":2}}',
                     '{"list":[{"run":null,"run":true}]}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                json.loads(text, object_pairs_hook=unique_object)

    def test_distinct_objects_same_key_and_null_retained(self):
        value = json.loads('{"before":{"source":1},"after":{"source":2},"nullable":null}', object_pairs_hook=unique_object)
        self.assertEqual(value, {'before': {'source': 1}, 'after': {'source': 2}, 'nullable': None})


if __name__ == '__main__': unittest.main()
