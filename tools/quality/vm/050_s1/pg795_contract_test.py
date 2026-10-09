"""Test assembled full profile without starting Maven or accepting actual native."""
import ast
import unittest
from pg794_completion_full import source as runner
from pg795_full_collect import source as collector


class Test(unittest.TestCase):
    def test_all_generated_surfaces_and_source_scope(self):
        text=collector();ast.parse(text)
        for required in ('3517, 289, None','suites == 520 and total_classes == 1620',"selected/'batch'/name",'pg793-selected-qualification-v1.safe.json','pg748-closing-six-host-v1','pg794-completion-six-host-v1','start <= original.stat().st_mtime <= end+1','flakyFailure','actual == classes(reference)'):
            self.assertIn(required,text)
        self.assertNotIn('pg711-expiry-core-v1',text)
        self.assertEqual(1,runner().count('pg794-completion-six-host-v1'))
        self.assertIn('sha256sum --check --status',runner());self.assertIn('clean spotless:check',runner())


if __name__=='__main__':unittest.main()
