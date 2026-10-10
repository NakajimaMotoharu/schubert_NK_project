"""Independent fixed before/epoch/approval/exchange/normal closure and golden contracts."""
import ast
import unittest
from pg1091_cold_activation_sources import files


class Activation(unittest.TestCase):
    def test_exact_new_family_mode_and_no_legacy_or_remount(self):
        value=files()
        self.assertEqual({'Pg1091ColdActivation.java','Pg1091ColdActivationTest.java','pg1091_cold_refs.py'},set(value))
        java=value['Pg1091ColdActivation.java'];py=value['pg1091_cold_refs.py']
        ast.parse(py)
        self.assertIn('"activate".equals(args[0])',java)
        self.assertIn("[b'Pg1091ColdActivation',b'activate',b'']",py)
        self.assertNotIn('freezeCandidate()',java)
        self.assertNotIn('refs.check("prepared")',java)
        self.assertIn('"epoch","approval","exchange","run"',java)
        self.assertNotIn('pg1084-cold-candidate-ro-v1',java)

    def test_real_publication_order_existing_api_and_independent_finite_io(self):
        value=files();java=value['Pg1091ColdActivation.java'];py=value['pg1091_cold_refs.py']
        names=['LEGITIMATE_EMPTY_INVALID','ATOMIC_APPROVAL','ATOMIC_EXCHANGE_LINKED_OLD']
        positions=[java.index('phase="'+name+'"')for name in names]
        self.assertEqual(sorted(positions),positions)
        self.assertIn('permits.invalidate(UUID.fromString(BOOT),fresh,ORIGINAL)',java)
        self.assertNotIn('permits.issue(',java)
        self.assertIn('StandardCopyOption.ATOMIC_MOVE',java)
        self.assertIn('candidate.encode()',java)
        self.assertIn("PHASE='link-staged';pair()",py)
        self.assertIn("exchange_io.exchange(current_fd,'pg1088-current.part')",py)
        self.assertIn("os.rename('pg1088-current.part','current-link.private'",py)
        self.assertIn('pub.verify_retained',py)
        self.assertIn('current_link',py.replace('current-link','current_link'))
        self.assertNotIn('unlink(',py.split('BODY',1)[-1])  # read-only/helper descriptions may contain words, not unlink calls


if __name__=='__main__':unittest.main()
