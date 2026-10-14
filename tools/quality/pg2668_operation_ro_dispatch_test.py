import unittest
from pg2668_operation_ro_dispatch import source,STAGE
from pg2672_operation_ro_post import payload
from pg2658_operation_candidate_sources import SOURCE,BOOT


class ReadonlyConnectionPreparation(unittest.TestCase):
    def test_exact_selected_source_and_actual_mount_namespace_post(self):
        raw=source()
        for m in ['2f7ca23be804567a5d9a61636cf4c1d4ec96fcd0','pg2667-frozen','pg2664-operation-unused-post-v1']:self.assertIn(m,raw)
        self.assertIn(BOOT,STAGE)
        post=payload({'actualExit':0,'candidateSource':SOURCE,'signatureVerified':True,'manifestSha256':'a'*64,'signatureSha256':'b'*64})
        for m in ['candidateHostReadonlyVerified','/proc/1/ns/mnt','0.1.0-PG2654','pg2670-operation-host-ro-v1']:self.assertIn(m,post)


if __name__=='__main__':unittest.main()
