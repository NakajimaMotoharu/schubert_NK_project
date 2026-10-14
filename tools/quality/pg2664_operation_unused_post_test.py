import unittest
from pg2664_operation_unused_post import payload,SLOT
from pg2658_operation_candidate_sources import SOURCE,SAVE,BEFORE


class NewUnusedPost(unittest.TestCase):
    def test_actual_current_reader_and_exact_candidate_separate(self):
        raw=payload({'actualExit':0,'candidateSource':SOURCE,'signatureVerified':True,'manifestSha256':'a'*64,'signatureSha256':'b'*64})
        for marker in [SLOT,SAVE,BEFORE,SOURCE,'pg2656-current-a79-before-v1/native-before.private.json','0.1.0-PG2654']:
            self.assertIn(marker,raw)
        self.assertNotIn("save=base/'pg2656-current-a79-before-v1'",raw)

    def test_foreign_candidate_or_unknown_digests_refused(self):
        for c in [{},{'actualExit':False},{'actualExit':0,'candidateSource':'foreign','signatureVerified':True}]:
            with self.assertRaises(ValueError):payload(c)


if __name__=='__main__':unittest.main()
