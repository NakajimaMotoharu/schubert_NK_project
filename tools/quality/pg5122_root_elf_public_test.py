"""Literal independent coverage identities and distinct same-target artifact paths."""
from pathlib import Path
import unittest
import pg5122_root_elf_public as role


class PublicCoverage(unittest.TestCase):
    def test_two_modules_are_never_one_target_key(self):
        root = Path('/fixture/source')
        a = root/'src/schubert-nk-batch/target/site/jacoco/jacoco.xml'
        b = root/'src/schubert-nk-storage/target/site/jacoco/jacoco.xml'
        result = role.coverage_hashes([a,b],root,lambda p:'a'*64 if p==a else'b'*64)
        self.assertEqual(result, {
            'src/schubert-nk-batch/target/site/jacoco/jacoco.xml':'a'*64,
            'src/schubert-nk-storage/target/site/jacoco/jacoco.xml':'b'*64})
        with self.assertRaises(ValueError): role.coverage_hashes([a,a],root,lambda _: 'a'*64)

    def test_new_cases_do_not_change_original_e8ec_case_set(self):
        self.assertEqual(len(role.GUARD_NAMES),3)
        self.assertEqual(len(role.FACTORY_GUARD_NAMES),4)
        self.assertEqual(len(set(role.FACTORY_NAMES)),12)
        self.assertEqual(len(set(role.DIRECTORY_NAMES)),3)


if __name__=='__main__':
    unittest.main()
