"""Pure exact-path/count generation check, no host or PT issue."""
import unittest
from pg5790_jms_whole_public import payload


class PublicReaderBinding(unittest.TestCase):
    def test_current_original_only_and_exact3939(self):
        raw=payload({});self.assertIn('source-full-PG5780',raw);self.assertIn('runs/PG5780-six-v1/manifest.safe.json',raw);self.assertIn('transfer/PG5780-source.tar',raw)
        self.assertIn('len(all_cases) != 3939',raw);self.assertNotIn('PG4968',raw);self.assertNotIn('subprocess.',raw)


if __name__=='__main__':unittest.main()
