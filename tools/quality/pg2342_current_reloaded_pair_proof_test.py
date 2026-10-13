import unittest
from pyflakes.api import check
from pg2342_current_reloaded_pair_proof_v2 import payload


class MetadataBoundary(unittest.TestCase):
    def test_actual_tuple_boundaries_and_whole_globals(self):
        raw=payload();self.assertEqual(0,check(raw,'<whole current tuple FD>'))
        self.assertIn("tuple(fds[n]['metadata'][2:4])==(0,0)",raw)
        self.assertIn("tuple(fds['9']['metadata'])==(28,4224",raw)
        for metadata in [(28,4224,0,0,33188,1,644,1791913648316105696,1791913648316105696),[28,4224,0,0,33188,1,644,1791913648316105696,1791913648316105696]]:
            self.assertEqual((0,0),tuple(metadata[2:4]))
            self.assertEqual((28,4224,0,0,33188,1,644,1791913648316105696,1791913648316105696),tuple(metadata))
        self.assertNotIn('pidfd_send_signal',raw)


if __name__=='__main__':unittest.main()
