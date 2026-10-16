import ast
import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg3816_hygiene_browser_composite as tool
import pg3818_hygiene_parent_projection as parent
import pg3806_hygiene_admission_before as before


class WholeComposite(unittest.TestCase):
    def test_chain_and_root_guard_never_rewritten(self):
        live=tool.actual.live();binding={**live['binding'],'rootPid':live['rootPid']}
        with patch.object(tool.root,'before',return_value=before.AFTER):original=tool.root.seal_payload(binding)
        historical={'run_id':'0dc63b79-3f9a-450c-b2a6-56f86272d272','source':'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25','activation':'0ac69fb7-3cb7-4d33-b2d9-4733fba5a4cf'}
        chain={'before':{'historical':[historical]},'after':{'historical':[historical]},'context':{}}
        raw=tool.compose(original,chain,'b'*64);self.assertEqual(0,check(raw,'<current whole composite>'))
        def constants(text):return{n.targets[0].id:n.value for n in ast.parse(text).body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
        values=constants(raw);oracle=ast.literal_eval(values['ORACLE']);inner=constants(oracle)
        self.assertEqual(chain,ast.literal_eval(inner['CHAIN']))
        self.assertEqual(ast.literal_eval(constants(original)['GUARD']),ast.literal_eval(values['GUARD']))
        for marker in [tool.SOURCE,tool.BOM,'/'+tool.root.SEAL+'/before.private.json',"require(new==CHAIN['after'])"]:self.assertTrue(marker in oracle,marker)
        projected=parent.payload('a'*64,tool.BOM);ast.parse(projected)
        self.assertIn(tool.SLOT,projected);self.assertIn(tool.SOURCE,projected)
        with self.assertRaises(ValueError):parent.payload('a'*64,'f'*64)


if __name__=='__main__':unittest.main()
