import unittest
from pg5988_web_contract_plan import private_source


class PrivateRecordConstantDeclarationTest(unittest.TestCase):
    def test_record_header_and_compact_constructor_remain_exact(self):
        original = 'public record SessionAttributes(\n    int count) {\n  public SessionAttributes {\n    if (count > 10) throw new IllegalArgumentException();\n  }\n}\n'
        after = private_source(original, [('if (count > 10)', 'if (count > MAXIMUM_COUNT)', 1)], ['private static final int MAXIMUM_COUNT = 10;'])
        self.assertEqual(original.replace('{\n  public SessionAttributes', '{\n  private static final int MAXIMUM_COUNT = 10;\n\n  public SessionAttributes', 1).replace('if (count > 10)', 'if (count > MAXIMUM_COUNT)'), after)
        self.assertNotIn('final class', after)

    def test_wrong_condition_or_existing_constant_never_rewritten(self):
        original = 'public final class A {\n  private static final int MAXIMUM_COUNT = 10;\n}\n'
        with self.assertRaises(ValueError):
            private_source(original, [('missing','new',1)], ['private static final int MAXIMUM_COUNT = 10;'])


if __name__ == '__main__':
    unittest.main()
