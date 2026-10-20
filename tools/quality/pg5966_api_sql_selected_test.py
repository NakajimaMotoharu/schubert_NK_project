import unittest
from pyflakes.api import check
import pg5966_api_sql_selected as t


class SqlExpressionSelectedDefinitionTest(unittest.TestCase):
    def test_annotation_parentheses_comments_literals_and_skips(self):
        source = '''// @Test void fake() {}
        class Example { String text = "@Test void fake2() {}";
        String sql = """@Test void fake3() {}""";
        @Test @Order(2) @DisplayName("literal (nested) parentheses")
        void real(@TempDir Path root) throws Exception {}
        }'''
        self.assertEqual({'real'}, t.ordinary_names(source))
        for bad in ('@Disabled class Example { @Test void a() {} }', '@TestFactory void a() {}', '@Test int a() {}', '@Test void a() {} @Test void a() {}'):
            with self.assertRaises(ValueError):
                t.ordinary_names(bad)

    def test_all_actual_case_sources_and_complete_generated_runner(self):
        cases, counts, targets = t.inventory()
        self.assertEqual(169, len(cases['api'])); self.assertEqual(1021, sum(counts.values())); self.assertEqual(175, len(counts)); self.assertEqual(16, len(targets['api']))
        raw = t.runner_source()
        names = sorted(k for k in vars(t.engine) if k.isidentifier() and not k.startswith('__') and k != 'main')
        self.assertEqual(0, check('='.join(names)+'=None\nCOUNTS=None\n'+raw, '<pure selected1021 namespace>'))
        self.assertIn('len(target_counters)==16', raw)
        self.assertIn("('LINE','METHOD','CLASS','BRANCH')", raw)
        self.assertNotIn('systemctl', raw); self.assertNotIn('qemu-system', raw)


if __name__ == '__main__':
    unittest.main()
