import unittest
from pg5822_current3955_public import payload


class ExactOriginal3955ProjectionTest(unittest.TestCase):
    def test_original_paths_counts_no_runtime_or_pt_call(self):
        raw=payload({})
        self.assertIn('source-full-PG5808',raw)
        self.assertIn('!= 3955',raw)
        self.assertNotIn('PG5780',raw)
        self.assertNotIn('subprocess',raw)
        self.assertNotIn('socket',raw)


if __name__=='__main__':unittest.main()
