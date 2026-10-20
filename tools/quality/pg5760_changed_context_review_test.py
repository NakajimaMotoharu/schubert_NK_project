"""Negative controls for review boundary, not Production PT or alternative PT."""
import unittest
from pg5760_changed_context_review import exact_scope,opcode


class ScopeBoundaryTest(unittest.TestCase):
    def test_native_tail_may_move_but_must_remain_exact(self):
        a='outer\n  static final class NativeIo implements Io {\nThread.sleep(1);\n}\n'
        self.assertEqual(1,exact_scope(a,'extra\n'+a,'NATIVE_IO'))
        with self.assertRaisesRegex(ValueError,'source tail'):exact_scope(a,a.replace('sleep(1)','sleep(2)'),'NATIVE_IO')
        with self.assertRaisesRegex(ValueError,'declaration'):exact_scope(a,a+a,'NATIVE_IO')

    def test_enum_model_rejects_external_behavior_change(self):
        p='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot.java'
        a='  public enum Target {\nprivate final String unit;\nthis.unit = unit;\nreturn unit;\n}\n  static final String UNIT = "one";'
        b=a.replace('String unit;','String systemUnit;').replace('this.unit =','this.systemUnit =').replace('return unit;','return systemUnit;')
        self.assertEqual(0,exact_scope(a,b,p))
        with self.assertRaisesRegex(ValueError,'bounded'):exact_scope(a,b.replace('"one"','"two"'),p)

    def test_opcode_normalizes_cp_spacing_not_branch_literals(self):
        self.assertEqual(opcode('3: ldc #10   // String x'),opcode('3: ldc #100 // String x'))
        self.assertNotEqual(opcode('3: ldc #10 // String x'),opcode('3: ldc #10 // String y'))
        self.assertNotEqual(opcode('3: goto 10'),opcode('3: goto 11'))


if __name__=='__main__':unittest.main()
