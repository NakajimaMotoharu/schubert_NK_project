import unittest
from pg1495_publication_recovery_once import valid_receipt

class RecoveryReceiptTest(unittest.TestCase):
    def test_exact_three_current_labels(self):
        v=b'PG1292 STAGE PINNED_SIGNATURE_VERIFIED\nPG1292 STAGE FULL_CANDIDATE_BOM_VERIFIED\nPG1495_DONE publicationOnlyRecovered=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false\n'
        self.assertTrue(valid_receipt(v))
        for bad in (None,v.decode(),v.splitlines(keepends=True)[2],v+b'extra\n',b'extra\n'+v,v.replace(b'PG1292',b'PGOLD'),v.replace(b'publicationOnlyRecovered=true',b'publicationOnlyRecovered=false'),v.replace(b'originalRetiredOrAuthorityIssued=false',b'originalRetiredOrAuthorityIssued=true'),v.replace(b'PG1495_DONE',b'OLD_ROOT_DONE'),v[:-1]):
            self.assertFalse(valid_receipt(bad))

if __name__=='__main__':unittest.main()
