import ast
import unittest
import pg3786_hygiene_ro_post as tool


class Post(unittest.TestCase):
    def test_all_independent_checks_preserved_and_ro_added_after_reference_close(self):
        raw=tool.payload();ast.parse(raw)
        for marker in ['cfg==oldcfg','read_rows()==first','candidate187SignatureVerified','newTenReferencesReturnedNormally','afterfile','allClientAdvisoryMA0','native34Preserved','findmnt',tool.role.SAVE]:self.assertTrue(marker in raw,marker)
        self.assertLess(raw.index('for unit in reversed(refs):'),raw.index("mount=subprocess.run(['findmnt'"))
        for forbidden in ['daemon-reload','systemctl start','systemctl stop']:self.assertNotIn(forbidden,raw)


if __name__=='__main__':unittest.main()
