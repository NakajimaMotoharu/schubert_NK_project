import ast
import unittest
from bundle_hash_contract import require_bound
import pg3788_hygiene_publication_sources as role
import pg3790_hygiene_publication_compile as compiler


class FiniteRoles(unittest.TestCase):
    def test_complete_roles_original_transition_data_and_bundle(self):
        values=role.sources();self.assertEqual(24,len(values));raw='\n'.join(values.values())
        for marker in [role.CURRENT,role.SOURCE,role.BEFORE,role.CURRENT_BOM,role.BOM,role.TOOLS,role.SAVE,role.ro.SAVE]:self.assertTrue(marker in raw,marker)
        for marker in ['NORMAL_DAEMON_RELOAD','REGULAR_MORNING_UNIT_EXCHANGE','pg3450','Pg3450','pg3446']:self.assertFalse(marker in raw,marker)
        current,_,ended=role.mapping.current_tuple()
        for name in [role.CLASS+'.java','Pg3788TransitionTest.java','pg3788_ordinary_publication_contract.py']:
            for value in [current['run'],current['activation']]:self.assertTrue(value in values[name],name)
        self.assertIn(ended,values['Pg3788TransitionTest.java'])
        bound=compiler.generated();require_bound(bound['pg3788_native_refs.py'],compiler.previous.sha(compiler.previous.PRIOR/'bundle.safe.json'))
        ast.parse(compiler.compiler());self.assertIn("('transition','TransitionTest')",compiler.compiler())
        for bom,before in [(None,role.BEFORE),(role.BOM,'f'*64)]:
            with self.assertRaises(ValueError):role.sources(bom,before)


if __name__=='__main__':unittest.main()
