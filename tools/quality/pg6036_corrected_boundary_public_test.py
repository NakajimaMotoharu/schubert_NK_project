import unittest
from pyflakes.api import check
import pg6036_corrected_boundary_public as t


class CorrectedIndependentXmlTest(unittest.TestCase):
    def test_whole_reader_namespace_and_no_failed_source_conversion(self):
        names = sorted(k for k in vars(t.previous) if k.isidentifier() and not k.startswith('__') and k != 'main')
        raw = t.reader_source()
        self.assertEqual(0, check('='.join(names)+'=None\n'+raw, '<new-source qualification full namespace>'))
        self.assertNotIn('pg6026-error-boundary-selected965-v1', raw)
        self.assertIn('originalSelectedOverallExit=0', raw)
        self.assertIn("'PT-PG6032-'", raw)


if __name__ == '__main__':
    unittest.main()
