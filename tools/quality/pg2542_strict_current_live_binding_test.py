import ast
import unittest
from pg2542_strict_current_live_binding import body


class CurrentIdentity(unittest.TestCase):
    def test_all_past_generations_are_explicitly_excluded(self):
        raw = body()
        ast.parse(raw)
        for value in ['PG2512', '06236d14-a6f8-4d05-a6ff-49c713cc2647',
                      'c347b14a-2e59-41e6-993c-a07e537cbd00',
                      '91f5484b-9702-4c7c-97f3-dd5110a853f9', 'e1429ac8-f3dd-4e8c-83d2-1926c4ba8440',
                      'a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75', '9026b2ab-bb42-49cd-a2bd-4c661049dce3']:
            self.assertIn(value, raw)
        self.assertNotIn('PG2428', raw)


if __name__ == '__main__':
    unittest.main()
