"""Independent exact output/dependency separation, no VM action."""
from pathlib import Path
import unittest
from pg685_compile_frozen import recipe


class RecipeTest(unittest.TestCase):
    def test_actual_dependencies_unchanged(self):
        raw = (Path(__file__).parent/'pg685_compile_v2.sh').read_text()
        actual = recipe(raw)
        self.assertEqual(next(x for x in raw.splitlines() if x.startswith('task_cp=')),
                         next(x for x in actual.splitlines() if x.startswith('task_cp=')))
        for name in ('pg464-code-tools-v2', 'pg481-pending-tools-v2'):
            self.assertIn(name, actual)
        for name in ('completed-tools', 'compile', 'oracle'):
            self.assertIn('pg685-'+name+'-v4', actual)
            self.assertNotIn('pg685-'+name+'-v2', actual)

    def test_missing_each_output_rejected(self):
        raw = (Path(__file__).parent/'pg685_compile_v2.sh').read_text()
        for name in ('completed-tools', 'compile', 'oracle'):
            with self.subTest(name=name), self.assertRaises(AssertionError):
                recipe(raw.replace('pg685-'+name+'-v2', 'foreign-output'))

    def test_duplicate_each_output_rejected(self):
        raw = (Path(__file__).parent/'pg685_compile_v2.sh').read_text()
        for name in ('completed-tools', 'compile', 'oracle'):
            with self.subTest(name=name), self.assertRaises(AssertionError):
                recipe(raw+'\n# pg685-'+name+'-v2\n')


if __name__ == '__main__':
    unittest.main()
