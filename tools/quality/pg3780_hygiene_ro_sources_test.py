import ast
import unittest
from bundle_hash_contract import assignments, require_bound
import pg3780_hygiene_ro_sources as role
import pg3782_hygiene_ro_compile as compiler


class RoRoles(unittest.TestCase):
    def test_full_roles_latest_completed_tuple_and_single_bundle(self):
        values=role.sources();self.assertEqual(18,len(values))
        self.assertFalse(assignments(values['pg3780_native_refs.py'])[1])
        bound=compiler.generated();require_bound(bound['pg3780_native_refs.py'],compiler.sha(compiler.PRIOR/'bundle.safe.json'))
        raw='\n'.join(values.values())
        for marker in [role.TOOLS,role.SAVE,role.CURRENT,role.SOURCE,role.BOM,role.BEFORE]:self.assertIn(marker,raw)
        latest=role.mapping.current_tuple()[0]
        self.assertEqual(latest,role.mapping.previous.binding(values['pg3780_parent_receipt.py']))
        for marker in [latest['activation'],latest['run']]:self.assertIn(marker,values['Pg3780CandidateRo.java'])
        self.assertNotIn('pg3442',raw);self.assertNotIn('Pg3442',raw)
        for value in values.values():
            if value.startswith('import ast'):ast.parse(value)
        for bom,before in [(None,role.BEFORE),(role.BOM,'f'*64)]:
            with self.assertRaises(ValueError):role.sources(bom,before)


if __name__=='__main__':unittest.main()
