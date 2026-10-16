import ast
import unittest
import pg3766_hygiene_unused_sources_v2 as c
import pg3768_hygiene_unused_compile_v2 as compiler
from bundle_hash_contract import assignments,require_bound


class V2(unittest.TestCase):
    def test_all18_and_only_two_bound_preludes_removed_then_one_actual_binding(self):
        values=c.sources();self.assertEqual(18,len(values))
        for name in ['pg3766_native_refs.py','pg3766_input_preflight.py']:
            raw=values[name];self.assertEqual([],assignments(raw)[1]);self.assertTrue(require_bound("BUNDLE_HASH='"+'b'*64+"'\n"+raw,'b'*64))
            with self.assertRaises(ValueError):require_bound("BUNDLE_HASH='"+'b'*64+"'\nBUNDLE_HASH='"+'a'*64+"'\n"+raw,'b'*64)
        expected=c.bind(c.old.pinned(c.old.LATEST,'Pg3600OriginalTupleTest.java').replace('Pg3600NativeStop','Pg3756UnusedStage').replace('Pg3600','Pg3756').replace('PG3600','PG3756'));self.assertEqual(expected,values['Pg3766OriginalTupleTest.java'])
        raw=compiler.compiler();ast.parse(raw)
        self.assertEqual(c.W/c.TOOLS,compiler.TARGET);self.assertEqual(c.ARCHIVE,compiler.ARCHIVE.name)
        for s in ['pg3768-frozen-v1','pg3748-release-v1','pg3420-release-v1']:self.assertIn(s,raw)
        self.assertNotIn('pg3756-',raw)


if __name__=='__main__':unittest.main()
