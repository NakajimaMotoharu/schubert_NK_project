import unittest
from pg2322_current_partial_runtime_pair_proof import payload


class PartialProof(unittest.TestCase):
    def test_exact_partial_runtime_and_current_pair_full_readonly(self):
        raw=payload()
        for value in ['98485','1656317','98516','1656547','98514','888ee8561e9c25da302470c2561cdbf65cbf10cdebf668f7196f27b485bc5035','reloadNotReserved','partialRuntimeFileVerified','len(rows) == 24','same_peer','fd_relation','1791913648315000000','pg2316-current-cold-resume-tools-v1']:
            self.assertTrue(value in raw,'missing partial-proof boundary '+value)
        for value in ['96640','96671','96669','pidfd_send_signal','SIGTERM','daemon-reload-reserved.private']:
            self.assertFalse(value in raw,'foreign or mutation '+value)


if __name__=='__main__':unittest.main()
