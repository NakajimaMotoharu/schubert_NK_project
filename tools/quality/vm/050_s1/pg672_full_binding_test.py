"""FULL672001 correct six membership, unchanged quality and fresh qualified namespace."""
import ast
import unittest
from pg672_full_v2 import source
from pg674_collect_full import source as collector


class Test(unittest.TestCase):
    def test_correct_membership_only_and_no_rule_changes(self):
        raw=source();expected='src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch'
        self.assertEqual(raw.count(' -pl '+expected+' '),1)
        for s in('pg672-entry-six-host-v2','qualified_nullable_check.py','spotless:check test-compile jar:test-jar test spotbugs:check jacoco:report jar:jar','source-files.sha256','--check --status','git status --porcelain'):
            self.assertIn(s,raw)
        for s in('pg672-entry-six-host-v1','jacoco.skip','maven.test.skip','skipTests','coverage.minimum','repository=','program/characterization'):
            self.assertNotIn(s,raw)
        c=collector();ast.parse(c)
        self.assertIn('pg672-entry-six-host-v2',c);self.assertNotIn('pg672-entry-six-host-v1',c)
        self.assertIn('suites == 514 and total_classes == 1608',c)


if __name__=='__main__':unittest.main()
